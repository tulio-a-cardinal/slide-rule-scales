from SlideRuleScale import SlideRuleScale
import os

os.chdir("./Example/")

Example = SlideRuleScale("./specs/scale/")
Example.set_scale_type("c", positioning_factor=0.01)
Example.draw_straight("./straight.svg", "./specs/draw_straight.csv")
Example.draw_circular("./circular.svg", "./specs/draw_circular.csv")
