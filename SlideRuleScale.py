import numpy as np
import pandas as pd
import svgwrite as sw


class SlideRuleScale:
    # Initializes by importing spec/scale data. This data includes which numbers or constants are represented and how
    def __init__(self, scale_specs_dir):

        print("\nImporting Scale Specs ...")

        # Reads core data. This data includes the main positions, in which the pattern for number representation changes
        filename = scale_specs_dir + "Core.csv"
        self.scale_spec = pd.read_csv(filename, dtype={"name": str})  # Reads name as string, not number
        self.scale_spec.insert(0, "position", self.scale_spec["name"].astype(float))  # Adds position column, from name

        # Get bounds and to conform name to the standard format
        bounds = []  # Initialise bounds variable
        prev_line = None  # Initialize auxiliary variable to get bounds
        # Iterates over each initial line
        for i, line in self.scale_spec.iterrows():
            # Extracts and organizes the bounds for each different sector with different number representation molds
            if i > 0:  # Extracts and organizes the bounds for each different sector
                bounds.append([prev_line["name"], line["name"]])
            prev_line = line
            # Edit name to conform to the standard format
            self.scale_spec.loc[i, "name"] = "{:.5f}".format(line["position"]).rstrip("0").rstrip(".")

        # Sets name column as index
        self.scale_spec.set_index("name", inplace=True)

        # Imports the data from each sector and works it to obtain positions and their respective representations
        # Iterates over each sector, represented by their bounds
        for bound in bounds:
            print(" -Working from " + bound[0] + " to " + bound[1] + " ...")

            # Reads mold data of sector from file name generated from bounds positions.
            # This data includes instructions on how to generate all represented numbers and how they should be shown
            filename = scale_specs_dir + bound[0] + "-" + bound[1] + ".csv"
            try:
                spec_molds = pd.read_csv(filename, dtype={"interval": str}).set_index("interval")
            except FileNotFoundError:
                print("   FILE NOT FOUND: " + filename + "\n   Empty file is assumed.")
                spec_molds = pd.DataFrame()
            # Works mold data to obtain the numbers and add them to self.scale_spec
            # Iterates over each row of the mold, from first to last
            for i, spec_mold in spec_molds.iterrows():
                # Extracts the desired value for the interval between two numbers
                # noinspection PyTypeChecker
                interval = float(spec_mold.name)
                # Sets first position of the sector defined by current row
                spec_mold["position"] = float(bound[0]) + interval
                # Sets name based on 5 digit approximation of position
                spec_mold.rename("{:.5f}".format(spec_mold["position"]).rstrip("0").rstrip("."), inplace=True)
                # Iterates over numbers until upper bound
                while spec_mold["position"] < float(bound[1]):
                    try:  # Only add number if it has not yet been added (PREFERENCE FOR FIRST ROWS OF MOLD)
                        self.scale_spec = self.scale_spec.append(spec_mold, verify_integrity=True)
                    except ValueError:  # If number has already been added, do nothing
                        pass
                    # Iterates position with step of size interval
                    spec_mold["position"] = spec_mold["position"] + interval
                    # Sets name based on 5 digit approximation of position
                    spec_mold.rename("{:.5f}".format(spec_mold["position"]).rstrip("0").rstrip("."), inplace=True)

        # Organises data, edits one-offs on data and reconfigures data
        print(" -Editing one-offs & Post processing ...")
        self.scale_spec.sort_values(by="position", inplace=True)  # Puts all numbers in order. Good for debugging
        # One-offs are added after ordering so that they are always prioritized
        filename = scale_specs_dir + "one-offs.csv"
        try:
            spec_one_offs = pd.read_csv(filename, dtype={"name": str}).set_index("name")
        except FileNotFoundError:
            print("   FILE NOT FOUND: " + filename + "\n   Empty file is assumed.")
            spec_one_offs = pd.DataFrame()
        self.scale_spec = self.scale_spec.append(spec_one_offs)  # Appends one-offs.csv data
        # Deletes any line that was in the same position as any of the one-offs that were just added
        self.scale_spec.drop_duplicates(subset="position", keep="last", inplace=True)
        self.scale_spec.reset_index(inplace=True)  # Removes names from index, leaving empty index (auto index)

        # Keeps track if scale was already set
        self.scale_set = False

    # Processes position values of scale_spec in accordance with:
    # - scale_type: scale types (Mannheim based)
    # - invert_scale: whether the scale should be inverted or not. E.g.: CI scale, S or T scales on back side
    # - positioning_factor: positions are multiplied by this number before log conversion. Usually the same as bounds[0]
    # - log_base: the base of the logarithm. Base 10 for the decimal number system
    # The position values of the main part of the scales go from 0 to 1
    def set_scale_type(self, scale_type, invert_scale=False, positioning_factor=1, log_base=10):

        # Checks if scale was already set. If so, stops. If not, marks as already set and continues
        if self.scale_set:
            print("\nUnable to set scale: Scale type already set !!!")
            return
        self.scale_set = True

        print("\nSetting scale ...")

        #  x | # -> log(#)
        if scale_type in ["C", "D", "c", "d"]:
            print(" -Scale: " + "C or D, Base scale")
            # Repositions scale in accordance with positioning_factor - BEFORE transformation
            self.scale_spec["position"] = self.scale_spec["position"] * positioning_factor
            # Applies scales' transformation
            # NO TRANSFORMATION - this is the base scale
        #  x² | √# -> log(#)
        elif scale_type in ["A", "B", "a", "b"]:
            print(" -Scale: " + "A or B, Squares scale")
            # Repositions scale in accordance with positioning_factor - BEFORE transformation
            self.scale_spec["position"] = self.scale_spec["position"] * positioning_factor
            # Applies scales' transformation (square root)
            self.scale_spec["position"] = np.power(self.scale_spec["position"], 1./2)
        #  x³ | ∛# -> log(#)
        elif scale_type in ["K", "k"]:
            print(" -Scale: " + "K, Cubes scale")
            # Repositions scale in accordance with positioning_factor -  BEFORE transformation
            self.scale_spec["position"] = self.scale_spec["position"] * positioning_factor
            # Applies scales' transformation (cube root)
            self.scale_spec["position"] = np.power(self.scale_spec["position"], 1./3)
        # arcsin(x) or arctan(x) or deg(x rad) | rad(# deg) -> log(#)
        elif scale_type in ["ST", "S,T", "S&T", "st", "s,t", "s&t"]:
            print(" -Scale: " + "ST or S,T or S&T, Small sines and tangents scale")
            # Applies scales' transformation (radian conversion)
            self.scale_spec["position"] = np.radians(self.scale_spec["position"])
            # Repositions scale in accordance with positioning_factor - AFTER transformation
            self.scale_spec["position"] = self.scale_spec["position"] * positioning_factor
        # arcsin(x) | sin(# deg) -> log(#)
        elif scale_type in ["S", "s"]:
            print(" -Scale: " + "S, Sine scale")
            # Applies scales' transformation (sine of degrees, np.sin input is in radians)
            self.scale_spec["position"] = np.sin(np.radians(self.scale_spec["position"]))
            # Repositions scale in accordance with positioning_factor - AFTER transformation
            self.scale_spec["position"] = self.scale_spec["position"] * positioning_factor
        # arctan(x) | tan(# deg) -> log(#)
        elif scale_type in ["T", "t"]:
            print(" -Scale: " + "T, Tangent scale")
            # Applies scales' transformation (tangent of degrees, np.tan input is in radians)
            self.scale_spec["position"] = np.tan(np.radians(self.scale_spec["position"]))
            # Repositions scale in accordance with positioning_factor - AFTER transformation
            self.scale_spec["position"] = self.scale_spec["position"] * positioning_factor
        # √(1-x²) | √(1-#²) -> log(#) | Used with right-angled triangles and to obtain cos from sin
        elif scale_type in ["P", "p"]:
            print(" -Scale: " + "P, Pythagorean scale")
            # Applies scales' transformation (square root of one minus the number squared)
            self.scale_spec["position"] = np.power(1 - np.power(self.scale_spec["position"], 2), 1./2)
            # Repositions scale in accordance with positioning_factor - AFTER transformation
            self.scale_spec["position"] = self.scale_spec["position"] * positioning_factor
        # log(x) | log_base ^ (#) -> log(#)
        elif scale_type in ["L", "Lg", "M", "l", "lg", "m"]:
            print(" -Scale: " + "L or Lg or M, Linear or logarithmic or mantissa scale")
            # Repositions scale in accordance with positioning_factor -  BEFORE transformation
            self.scale_spec["position"] = self.scale_spec["position"] * positioning_factor
            # Applies scales' transformation (log_base to the power of)
            self.scale_spec["position"] = np.power(log_base, self.scale_spec["position"])
        # Not programed scale
        else:
            raise ValueError("Unknown scale type: '" + scale_type + "'")

        # Applies log with base log_base, and rounds final result to avoid issues with bounds and coincidence checks
        print(" -Log base: " + str(log_base))
        self.scale_spec["position"] = round(np.log(self.scale_spec["position"]) / np.log(log_base), 10)

        # Inverts scale if requested
        if bool(invert_scale):
            print(" -Inverted scale")
            self.scale_spec["position"] = 1.0 - self.scale_spec["position"]

        # Checks and warns about off scale positions
        bounds_index = [np.argmin(self.scale_spec["position"]), np.argmax(self.scale_spec["position"])]
        off_scale_warnings = []

        if self.scale_spec["position"][bounds_index[0]] < 0:
            off_scale_warnings.append(["lower", self.scale_spec["name"][bounds_index[0]],
                                       "under the minimum", str(-self.scale_spec["position"][bounds_index[0]])])
        elif self.scale_spec["position"][bounds_index[0]] > 1:
            off_scale_warnings.append(["lower", self.scale_spec["name"][bounds_index[0]],
                                       "over the maximum", str(self.scale_spec["position"][bounds_index[0]] - 1)])
        if self.scale_spec["position"][bounds_index[1]] < 0:
            off_scale_warnings.append(["upper", self.scale_spec["name"][bounds_index[1]],
                                       "under the minimum", str(-self.scale_spec["position"][bounds_index[1]])])
        elif self.scale_spec["position"][bounds_index[1]] > 1:
            off_scale_warnings.append(["upper", self.scale_spec["name"][bounds_index[1]],
                                       "over the maximum", str(self.scale_spec["position"][bounds_index[1]] - 1)])
        for off_scale_warning in off_scale_warnings:
            print(" -Unexpected " + off_scale_warning[0] + " bound")
            print("   of value " + off_scale_warning[1])
            print("   located " + off_scale_warning[2] + " by " + off_scale_warning[3])

        if not off_scale_warnings:
            print(" -Bounds OK")

    # Draws a straight scale based on the scale spec and its draw specs
    def draw_straight(self, output, draw_specs):

        if not self.scale_set:
            print("\nUnable to draw scale: scale type not set !!!")
            return

        print("\nDrawing straight scale ...")

        # Sets local variables from draw specs
        draw_specs = pd.read_csv(draw_specs).loc[0]
        paper_size_x = draw_specs["paper_size_x"]
        paper_size_y = draw_specs["paper_size_y"]
        scale_size_x = draw_specs["scale_size_x"]
        scale_origin_x = draw_specs["scale_origin_x"]
        scale_origin_y = draw_specs["scale_origin_y"]
        mark_origin_y = draw_specs["mark_origin_y"]
        line_width = draw_specs["line_width"]
        strip_zeros = draw_specs["strip_zeros"]

        # Creates svg with appropriate dimensions and all units in mm
        drawing = sw.Drawing(
            filename=output,
            size=(str(paper_size_x) + "mm", str(paper_size_y) + "mm"),
            viewBox="0 0 " + str(paper_size_x) + " " + str(paper_size_y)
            )

        # Adds a baseline for the scale, with size and width in accordance to draw specs
        drawing.add(drawing.line(
            start=(scale_origin_x, paper_size_y - scale_origin_y),
            end=(scale_origin_x + scale_size_x, paper_size_y - scale_origin_y),
            stroke_width=str(line_width),
            stroke="black"
            ))

        # Adds a mark line, with size and width in accordance to draw specs
        drawing.add(drawing.line(
            start=(scale_origin_x, paper_size_y - mark_origin_y),
            end=(scale_origin_x + scale_size_x, paper_size_y - mark_origin_y),
            stroke_width=str(line_width),
            stroke="black"
        ))

        # Iterates over each position in the created scale spec
        for i, line in self.scale_spec.iterrows():
            # Calculates x and y positions for base of line ([0]) and for tip of line ([1])
            x = [scale_origin_x + line["position"] * scale_size_x, scale_origin_x + line["position"] * scale_size_x]
            y = [scale_origin_y + line["l_position_base"], scale_origin_y + line["l_position_tip"]]
            # Adds the line. Converts the y position from being measured from the bottom to being measured from the top
            drawing.add(drawing.line(
                start=(x[0], paper_size_y - y[0]),
                end=(x[1], paper_size_y - y[1]),
                stroke_width=line["l_width"],
                stroke="black"
                ))

            # Checks if any text properties are NaN. If so, jumps text adding code. If not, executes text adding code
            if line[line.index.str.startswith("t_")].isnull().values.any():
                continue

            # Strips the zeros from the name, if specified
            if bool(strip_zeros):
                line["name"] = line["name"].rstrip("0")

            # Adds the text. Converts the y position from being measured from the bottom to being measured from the top
            # First positions then rotates text in accordance with its properties.
            # Then positions text at tip of line
            # (inverted order of operations relative to commands order below)
            drawing.add(drawing.text(
                line["name"],
                insert=(0, 0),
                transform="translate(" +
                          str(x[1]) + " " +
                          str(paper_size_y - y[1]) + ") "
                          "rotate(" + str(-line["t_angle"]) + ") "
                          "translate(" +
                          str(line["t_position_x"]) + " " +
                          str(-line["t_position_y"]) + ") ",
                fill="black",
                style="font-size:" + str(line["t_size"]) + ";"
                      "text-anchor:" + line["t_anchor"] + ";"
                      "font-family:" + line["t_font"]
                ))

        # Saves file
        drawing.save()
        print()  # New line after drawing is complete

    # Draws a full circular scale based on the scale spec and its draw specs
    def draw_circular(self, output, draw_specs):

        if not self.scale_set:
            print("\nUnable to draw scale: scale type not set !!!")
            return

        print("\nDrawing circular scale ...")

        # Sets positions from 0 to 1 only (the circle goes from 0 to 1 and repeats)
        self.scale_spec["position"] = self.scale_spec["position"] % 1
        # Erases lines with coincident positions (multiple runs around the circle could be the cause)
        self.scale_spec.drop_duplicates(subset="position", keep="last", inplace=True)

        # Sets local variables from draw specs. Paper is a square of sides paper_size
        draw_specs = pd.read_csv(draw_specs).loc[0]
        paper_size = draw_specs["paper_size"]
        limit_radius = draw_specs["limit_radius"]
        scale_radius = draw_specs["scale_radius"]
        mark_radius = draw_specs["mark_radius"]
        centermark_size = draw_specs["centermark_size"]
        line_width = draw_specs["line_width"]
        strip_zeros = draw_specs["strip_zeros"]
        # Defines center of circle at center of paper
        center = paper_size / 2

        # Creates svg with appropriate dimensions and all units in mm
        drawing = sw.Drawing(
            filename=output,
            size=(str(paper_size) + "mm", str(paper_size) + "mm"),
            viewBox="0 0 " + str(paper_size) + " " + str(paper_size)
            )

        # Adds a limit circle at the limit of the scale, with width in accordance to draw specs
        drawing.add(drawing.circle(
            center=(center, center),
            r=limit_radius,
            stroke_width=line_width,
            stroke="black",
            fill="none"
        ))

        # Adds a base circle for the scale, with size and width in accordance to draw specs
        drawing.add(drawing.circle(
            center=(center, center),
            r=scale_radius,
            stroke_width=line_width,
            stroke="black",
            fill="none"
            ))

        # Adds a mark circle, with size and width in accordance to draw specs
        drawing.add(drawing.circle(
            center=(center, center),
            r=mark_radius,
            stroke_width=line_width,
            stroke="black",
            fill="none"
            ))

        # Adds two lines marking the center, with size and width in accordance to draw specs
        drawing.add(drawing.line(
            start=(center - centermark_size / 2, center),
            end=(center + centermark_size / 2, center),
            stroke_width=line_width,
            stroke="black"
            ))
        drawing.add(drawing.line(
            start=(center, center - centermark_size / 2),
            end=(center, center + centermark_size / 2),
            stroke_width=line_width,
            stroke="black"
            ))

        # Iterates over each position in the created scale spec
        for i, line in self.scale_spec.iterrows():
            # Calculates r (radius) positions for base of line ([0]) and for tip of line ([1])
            r = [scale_radius + line["l_position_base"], scale_radius + line["l_position_tip"]]
            # Calculates theta (angle) position for the line
            theta = np.pi / 2 - line["position"] * 2 * np.pi
            # Converts (r, theta) to x and y positions for base of line ([0]) and for tip of line ([1])
            x = r * np.cos([theta]) + [center]
            y = r * np.sin([theta]) + [center]

            # Adds the line. Converts the y position from being measured from the bottom to being measured from the top
            drawing.add(drawing.line(
                start=(x[0], 2 * center - y[0]),
                end=(x[1], 2 * center - y[1]),
                stroke_width=line["l_width"],
                stroke="black"
                ))

            # Checks if any text properties are NaN. If so, jumps text adding code. If not, executes text adding code
            if line[line.index.str.startswith("t_")].isnull().values.any():
                continue

            # Strips the zeros from the end of the name, if specified
            if bool(strip_zeros):
                line["name"] = line["name"].rstrip("0")

            # Adds the text. Converts the y position from being measured from the bottom to being measured from the top
            # First positions then rotates text in accordance with its properties.
            # Then rotates text to line angle, plus 90°, for vertical line reference and horizontal text reference
            # Then positions text at tip of line
            # (inverted order of operations relative to commands order below)
            drawing.add(drawing.text(
                line["name"],
                insert=(0, 0),
                transform="translate(" +
                          str(x[1]) + " " +
                          str(2 * center - y[1]) + ") "
                          "rotate(" + str(-np.degrees(theta) + 90) + ") "
                          "rotate(" + str(-line["t_angle"]) + ") "
                          "translate(" +
                          str(line["t_position_x"]) + " " +
                          str(-line["t_position_y"]) + ") ",
                fill="black",
                style="font-size:" + str(line["t_size"]) + ";"
                      "text-anchor:" + line["t_anchor"] + ";"
                      "font-family:" + line["t_font"]
                ))

        # Saves file
        drawing.save()
        print()  # New line after drawing is complete

    # Outputs the scale spec in a csv file
    def debug_output_full_scale_spec(self):
        self.scale_spec.to_csv("DEBUG_scale_spec.csv")
