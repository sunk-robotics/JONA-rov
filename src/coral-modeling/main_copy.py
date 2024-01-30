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
    # center to center length
    length = 332.111
    # center to center height
    height = 132.165

    # total height 160.054
    # total length 360.000
    # padding 13.945
    return (
        Workplane("YZ")
        .rect(length, height, forConstruction=True)
        .vertices()
        # pvc radius
        .circle(10.766)
        .extrude(length)
    )


def right_tubes(length: int) -> Workplane:
    length = 332.111
    height = 290.805

    # total height 318.694
    # total length 360.000
    return (
        Workplane("YZ")
        .rect(length, height, forConstruction=True)
        .vertices()
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


#  from cadquery import Workplane, Assembly, Location, Vector, Color

#  height = 60.0
#  width = 80.0
#  thickness = 10.0
#  hole_diameter = 22.0
#  padding = 12.0


#  points = [(0, 0), (28, 0), (28, 20), (20, 20)]

# make the base
#  result = (
#      cq.Workplane("XY")
#      .box(height, width, thickness)
#      .faces(">Z")
#      .workplane()
#      .hole(hole_diameter)
#      .faces(">Z")
#      .workplane()
#      .rect(height - padding, width - padding, forConstruction=True)
#      .vertices()
#      .cboreHole(2.4, 4.4, 2.1)
#      .edges("|Z")
#      .fillet(2.0)
# )

#  result = cq.Workplane("XY").polyline(points).close().extrude(10)
#  result = cq.Workplane("YZ").circle(1).extrude(10)

#  width = 10
#  depth = 10
#  height = 10

#  part1 = Workplane().box(2 * width, 2 * depth, height)
#  part2 = Workplane().box(width, depth, 2 * height)
#  part3 = Workplane().box(width, depth, 3 * height)

#  assembly = (
#      Assembly(part1, loc=Location(Vector(-width, 0, height / 2)))
#  .add(
#      part2,
#      loc=Location(Vector(1.5 * width, -0.5 * depth, height / 2)),
#      color=Color(0, 0, 1, 0.5),
#  )
#  .add(
#      part3,
#      loc=Location(Vector(-0.5 * width, -0.5 * depth, 2 * height)),
#      color=Color("red"),
#  )
# )


left_length = 450
right_length = 600
top_height = 600

left_side_length = 60
left_side_width = 360
left_side_height = 160
left_side = Workplane().box(
    left_side_length, left_side_width, left_side_height
)
left_side = importers.importStep("assets/left_side.step")

right_side_length = 60
right_side_width = 360
right_side_height = 320
right_side = Workplane().box(
    right_side_length, right_side_width, right_side_height
)
right_side = importers.importStep("assets/right_side.step")

center_box_length = 410
center_box_width = 360
center_box_height = 400
center_box = Workplane().box(
    center_box_length, center_box_width, center_box_height
)
center_box = importers.importStep("assets/center_box.step")

top_side_length = 360
top_side_width = 410
top_side_height = 60
top_side = Workplane().box(top_side_length, top_side_width, top_side_height)
#  top_side = importers.importStep("assets/top_side.step")

assembly = (
    Assembly()
    .add(
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
    .add(
        left_side,
        name="left_side",
        #  loc=Location(
        #      Vector(
        #          -(center_box_length / 2 + left_side_length / 2 + left_length),
        #          -(left_side_width / 2),
        #          -(center_box_height / 2 - left_side_height / 2),
        #      )
        #  ),
        color=Color("green"),
    )
    .add(
        right_side,
        name="right_side",
        #  loc=Location(
        #      Vector(
        #          center_box_length / 2 + right_side_length / 2 + right_length,
        #          -(right_side_width / 2),
        #          -(center_box_height / 2 - right_side_height / 2),
        #      )
        #  ),
    )
    .add(left_tubes(60), name="left_tubes")
    #  .add(right_tubes(80), name="right_tubes")
)

assembly.constrain(
    "right_side@vertices@>(1, -1, -1)",
    "center_box@vertices@>(1, -1, -1)",
    "Point",
)
assembly.constrain(
    "left_side@vertices@>(-1, -1, -1)",
    "center_box@vertices@>(-1, -1, -1)",
    "Point",
)
assembly.constrain(
    "left_tubes@vertices@>(1, -1, -1)",
    "center_box@vertices@>(-1, -1, -1)",
    "Point",
)
assembly.constrain(
    "left_tubes@faces@<X", "center_box@faces@<X", "Axis", param=0
)
assembly.constrain(
    "left_tubes@faces@<Z", "center_box@faces@<Z", "Axis", param=90
)

assembly.constrain(
    "left_side@faces@<X", "center_box@faces@<X", "Axis", param=0
)
assembly.constrain(
    "left_side@faces@<Z", "center_box@faces@<Z", "Axis", param=0
)
assembly.constrain(
    "right_side@faces@<X", "center_box@faces@<X", "Axis", param=0
)
assembly.constrain(
    "right_side@faces@<Z", "center_box@faces@<Z", "Axis", param=0
)

start_time = time.time()
assembly.solve()
end_time = time.time()
print(f"Solved in {end_time - start_time}s")
#  w = 10
#  d = 10
#  h = 10

#  part1 = Workplane().box(2 * w, 2 * d, h)
#  part2 = Workplane().box(w, d, 2 * h)
#  part3 = Workplane().box(w, d, 3 * h)

#  assembly = (
#      Assembly(ooga, name="ooga", loc=Location(Vector(0, 0, 0)))
#      .add(booga, name="booga")
#      .constrain("ooga@faces@>Z", "booga@faces@<Z", "Axis")
#      .solve()
#  )

#  assembly = (
#      Assembly(part1, name="part1", loc=Location(Vector(-w, 0, h / 2)))
#      .add(part2, name="part2", color=Color(0, 0, 1, 0.5))
#      .add(part3, name="part3", color=Color("red"))
#      .constrain("part1@faces@>Z", "part3@faces@<Z", "Axis")
#      .constrain("part1@faces@>Z", "part2@faces@<Z", "Axis")
#      .constrain("part1@faces@>Y", "part3@faces@<Y", "Axis")
#      .constrain("part1@faces@>Y", "part2@faces@<Y", "Axis")
#      .constrain("part1@vertices@>(-1,-1,1)", "part3@vertices@>(-1,-1,-1)", "Point")
#      .constrain("part1@vertices@>(1,-1,-1)", "part2@vertices@>(-1,-1,-1)", "Point")
#      .solve()
#  )

#  ooga = Workplane().box(1, 2, 1)
#  booga = Workplane().box(5, 5, 5)
#  unga = Workplane("XZ").circle(1).extrude(5)
#  assembly = (
#      Assembly()
#      .add(ooga, name="ooga")
#      .add(booga, name="booga")
#      #  .add(unga, name="unga")
#      .constrain("ooga@faces@>X", "booga@faces@<X", "Plane")
#      .constrain("ooga@faces@<Z", "booga@faces@>Z", "Plane")
#      .solve()
#  )

#  plate = Workplane().box(10, 10, 1).faces(">Z").workplane().hole(2)
#  cone = Solid.makeCone(0.8, 0, 4)

#  assembly = (
#      Assembly()
#      .add(plate, name="plate", color=Color("green"))
#      .add(cone, name="cone", color=Color("blue"))
#      # place the center of the flat face of the cone in the center of the top face of the plate
#      .constrain("plate@faces@>Z", "cone@faces@<Z", "Point")
#      # set both the flate face of the cone and the upper face of the plate to point in the same direction
#      .constrain("plate@faces@>Z", "cone@faces@<Z", "Axis", param=0)
#      .solve()
#  )

#  box = Workplane().box(1, 1, 1)
#  ball = Workplane().sphere(0.15)

#  assembly = (
#      Assembly()
#      .add(box, name="box1")
#      .add(ball, name="ball", loc=Location((0, 0, 4)), color=Color("blue"))
#      .add(box, name="box2", loc=Location((-2, 0, 0)), color=Color("red"))
#  )

#  point = (0.5, 0, -0.5)

#  # fix the position of box1
#  assembly.constrain("box1", "Fixed")
#  # fix the ball at the point
#  assembly.constrain("ball", "FixedPoint", point)
#  assembly.constrain("box2@edges@<Z", "FixedPoint", point)
#  assembly.constrain("box1@faces@<Z", "box2@faces@<Z", "Axis", param=0)
#  assembly.constrain("box1@faces@<Y", "box2@faces@<Y", "Axis", param=0)

#  assembly.solve()


#  compound = assembly.toCompound()
#  exporters.export(compound, "result.glb")
#  exporters.export(assembly.toCompound(), "result.ply")
#  assembly.save("result.step")
assembly.save("result.stl")

#  exporters.export(assembly, "result.stl")
