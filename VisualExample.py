from SlideRuleScale import SlideRuleScale
import os

os.chdir("./VisualExample/")
# Scales go from the outer part to the inner, from most important to least important

to_do_list = ["Obverse1", "Obverse2", "Obverse3", "Obverse4", "Obverse5",
              "Reverse1", "Reverse2", "Reverse3", "Reverse4", "Reverse5"]
print("-------------------------------------------")

# ---OBVERSE---
if "Obverse1" in to_do_list:
    print("Obverse1")  # Fixed main scale
    Obverse1 = SlideRuleScale("./specs_obverse1/scale/")
    Obverse1.set_scale_type("c", positioning_factor=0.1)
    Obverse1.draw_circular("./Obverse1.svg", "./specs_obverse1/draw.csv")
    print("-------------------------------------------")

if "Obverse2" in to_do_list:
    print("Obverse2")  # Movable main scale
    Obverse2 = SlideRuleScale("./specs_obverse2/scale/")
    Obverse2.set_scale_type("c", positioning_factor=0.1)
    Obverse2.draw_circular("./Obverse2.svg", "./specs_obverse2/draw.csv")
    print("-------------------------------------------")

if "Obverse3" in to_do_list:
    print("Obverse3")  # Inverted scale
    Obverse3 = SlideRuleScale("./specs_obverse3/scale/")
    Obverse3.set_scale_type("c", invert_scale=True, positioning_factor=0.1)
    Obverse3.draw_circular("./Obverse3.svg", "./specs_obverse3/draw.csv")
    print("-------------------------------------------")

if "Obverse4" in to_do_list:
    print("Obverse4")  # Squares scale
    Obverse4 = SlideRuleScale("./specs_obverse4/scale/")
    Obverse4.set_scale_type("a", positioning_factor=0.1)
    Obverse4.draw_circular("./Obverse4.svg", "./specs_obverse4/draw.csv")
    print("-------------------------------------------")

if "Obverse5" in to_do_list:
    print("Obverse5")  # Cubes scale
    Obverse5 = SlideRuleScale("./specs_obverse5/scale/")
    Obverse5.set_scale_type("k", positioning_factor=0.1)
    Obverse5.draw_circular("./Obverse5.svg", "./specs_obverse5/draw.csv")
    print("-------------------------------------------")

# ---REVERSE---
if "Reverse1" in to_do_list:
    print("Reverse1")  # Sines scale | sin(5.73917047726679°)≈0.1
    Reverse1 = SlideRuleScale("./specs_reverse1/scale/")
    Reverse1.set_scale_type("s", invert_scale=True, positioning_factor=10)
    Reverse1.draw_circular("./Reverse1.svg", "./specs_reverse1/draw.csv")
    print("-------------------------------------------")

if "Reverse2" in to_do_list:
    print("Reverse2")  # Tangents scale | tan(5.71059313749964°)≈0.1
    Reverse2 = SlideRuleScale("./specs_reverse2/scale/")
    Reverse2.set_scale_type("t", invert_scale=True, positioning_factor=10)
    Reverse2.draw_circular("./Reverse2.svg", "./specs_reverse2/draw.csv")
    print("-------------------------------------------")

if "Reverse3" in to_do_list:
    print("Reverse3")  # Small sines and tangents scale | 5.72957795130823°≈1rad
    Reverse3 = SlideRuleScale("./specs_reverse3/scale/")
    Reverse3.set_scale_type("st", invert_scale=True, positioning_factor=100)
    Reverse3.draw_circular("./Reverse3.svg", "./specs_reverse3/draw.csv")
    print("-------------------------------------------")

if "Reverse4" in to_do_list:
    print("Reverse4")  # Pythagorean scale | √(1-0.994987437106620²)≈0.1
    Reverse4 = SlideRuleScale("./specs_reverse4/scale/")
    Reverse4.set_scale_type("p", invert_scale=True, positioning_factor=10)
    Reverse4.draw_circular("./Reverse4.svg", "./specs_reverse4/draw.csv")
    print("-------------------------------------------")

if "Reverse5" in to_do_list:
    print("Reverse5")  # Linear scale
    Reverse5 = SlideRuleScale("./specs_reverse5/scale/")
    Reverse5.set_scale_type("l", invert_scale=True, positioning_factor=0.1)
    Reverse5.draw_circular("./Reverse5.svg", "./specs_reverse5/draw.csv")
    print("-------------------------------------------")
