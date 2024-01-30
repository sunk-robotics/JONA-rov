import time
from cadquery import (
    exporters,
    importers,
    Assembly,
    Color,
    Location,
    Plane,
    Solid,
    Vector,
    Workplane,
)


def left_tubes(length: int) -> Workplane:
    # center to center width
    width = 332.111
    # center to center height
    height = 132.165

    total_width = 360.0
    total_height = 160.054

    # total height 160.054
    # total width 360.000
    # padding 13.945
    rv = (
        Workplane("YZ")
        .rect(width, height, forConstruction=True)
        .vertices("<Y and <X")
        .tag("bottom_left")
        .end()
        .vertices()
        # pvc radius
        .circle(10.766)
        .extrude(-length)
    )
    return rv


def right_tubes(length: int) -> Workplane:
    length = 332.111
    height = 290.805

    # total height 318.694
    # total length 360.000
    return (
        Workplane("YZ")
        .rect(length, height, forConstruction=True)
        .circle(12)
        .extrude(-length)
    )


def top_tubes(length: int) -> Workplane:
    # center to center length
    length = 346.5
    # center to center width
    width = 332.111

    # total length 374.389
    # total width 360.000

    return (
        Workplane("YZ")
        .rect(length, height, forConstruction=True)
        .vertices()
        .circle(12)
        .extrude(-length)
    )


#  left_length = 450
#  right_length = 600
#  top_height = 600

#  left_side_length = 60
#  left_side_width = 360
#  left_side_height = 160
#  left_side = Workplane().box(
#      left_side_length, left_side_width, left_side_height
#  )
start_time = time.time()
left_side = importers.importStep("assets/left_side.step")

#  right_side_length = 60
#  right_side_width = 360
#  right_side_height = 320
#  right_side = Workplane().box(
#      right_side_length, right_side_width, right_side_height
#  )
right_side = importers.importStep("assets/right_side.step")

#  center_box_length = 410
#  center_box_width = 360
#  center_box_height = 400
#  center_box = Workplane().box(
#      center_box_length, center_box_width, center_box_height
#  )
center_box = importers.importStep("assets/center_box.step")
end_time = time.time()
print(f"Imported in {end_time - start_time}s")

#  top_side_length = 360
#  top_side_width = 410
#  top_side_height = 60
#  top_side = Workplane().box(top_side_length, top_side_width, top_side_height)
#  top_side = importers.importStep("assets/top_side.step")

start_time = time.time()
assembly = (
    Assembly().add(
        center_box,
        name="center_box",
        loc=Location(Vector(0, 0, 0)),
        color=Color("red"),
    )
    #  .add(
    #      top_side,
    #      name="top_side",
    #      loc=Location(
    #          Vector(0, 0, center_box_height / 2 + top_side_height / 2 + top_height)
    #      ),
    #      color=Color("teal"),
    #  )
    #  .add(
    #      left_side,
    #      name="left_side",
    #      #  loc=Location(
    #      #      Vector(
    #      #          -(center_box_length / 2 + left_side_length / 2 + left_length),
    #      #          -(left_side_width / 2),
    #      #          -(center_box_height / 2 - left_side_height / 2),
    #      #      )
    #      #  ),
    #      color=Color("green"),
    #  )
    #  .add(
    #      right_side,
    #      name="right_side",
    #      #  loc=Location(
    #      #      Vector(
    #      #          center_box_length / 2 + right_side_length / 2 + right_length,
    #      #          -(right_side_width / 2),
    #      #          -(center_box_height / 2 - right_side_height / 2),
    #      #      )
    #      #  ),
    #  )
    .add(left_tubes(200), name="left_tubes")
    #  .add(right_tubes(80), name="right_tubes")
)
end_time = time.time()
print(f"Assembled in {end_time - start_time}s")

start_time = time.time()
#  assembly.constrain(
#      "right_side@vertices@>(1, -1, -1)",
#      "center_box@vertices@>(1, -1, -1)",
#      "Point",
#  )
#  assembly.constrain(
#      "left_side@vertices@>(-1, -1, -1)",
#      "left_tubes@vertices@>(-1, -1, -1)",
#      "Point",
#  )

assembly.constrain("center_box", "Fixed")
#  assembly.constrain(
#      "left_tubes@vertices@>(1, -1, -1)",
#      "center_box@vertices@>(-1, -1, -1)",
#      "Point",
#  )
#  assembly.constrain(
#      "left_tubes@edges@>X and <Z",
#      "center_box@vertices@>(-1, 1, -1)",
#      "Point",
#  )
assembly.constrain(
    "left_tubes?bottom_left", "center_box@vertices@>(-1, -1, -1)", "Point"
)
assembly.constrain("left_tubes", "FixedRotation", (0, 0, 0))
#  assembly.constrain(
#      "left_tubes@vertices@>(1, 1, -1)",
#      "center_box@vertices@>(-1, 1, -1)",
#      "Point",
#  )
#  assembly.constrain(
#      "left_tubes@faces@<X", "center_box@faces@<X", "Axis", param=0
#  )
#  assembly.constrain(
#      "left_tubes@faces@<Y", "center_box@faces@<Y", "Axis", param=90
#  )
#  assembly.constrain(
#      "left_tubes@faces@<Z", "center_box@faces@<Z", "Axis", param=90
#  )

#  assembly.constrain(
#      "left_side@faces@<X", "center_box@faces@<X", "Axis", param=0
#  )
#  assembly.constrain(
#      "left_side@faces@<Z", "center_box@faces@<Z", "Axis", param=0
#  )
#  assembly.constrain(
#      "right_side@faces@<X", "center_box@faces@<X", "Axis", param=0
#  )
#  assembly.constrain(
#      "right_side@faces@<Z", "center_box@faces@<Z", "Axis", param=0
#  )
end_time = time.time()
print(f"Constrained in {end_time - start_time}")

start_time = time.time()
assembly.solve()
end_time = time.time()
print(f"Solved in {end_time - start_time}s")

assembly.save("result.stl")


#  exporters.export(assembly, "result.stl")
