#  import cadquery as cq
from cadquery import exporters, importers, Workplane, Assembly, Location, Vector, Color

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
left_side = Workplane().box(left_side_length, left_side_width, left_side_height)
left_side = importers.importStep("left_side_centered.step")
print(left_side)

right_side_length = 60
right_side_width = 360
right_side_height = 320
right_side = Workplane().box(right_side_length, right_side_width, right_side_height)
right_side = importers.importStep("right_side.step")

center_box_length = 410
center_box_width = 360
center_box_height = 400
center_box = Workplane().box(center_box_length, center_box_width, center_box_height)

top_side_length = 360
top_side_width = 410
top_side_height = 60
top_side = Workplane().box(top_side_length, top_side_width, top_side_height)

#  booga = Workplane().circle(5).extrude(5)


assembly = (
    Assembly()
    .add(
        center_box, name="center_box", loc=Location(Vector(0, 0, 0)), color=Color("red")
    )
    .add(
        top_side,
        name="top_side",
        loc=Location(
            Vector(0, 0, center_box_height / 2 + top_side_height / 2 + top_height)
        ),
        color=Color("teal"),
    )
    .add(
        left_side,
        name="left_side",
        loc=Location(
            Vector(
                -(center_box_length / 2 + left_side_length / 2 + left_length),
                -(left_side_width / 2),
                -(center_box_height / 2 - left_side_height / 2),
            )
        ),
        color=Color("green"),
    )
    .add(
        right_side,
        name="right_side",
        loc=Location(
            Vector(
                center_box_length / 2 + right_side_length / 2 + right_length,
                -(right_side_width / 2),
                -(center_box_height / 2 - right_side_height / 2),
            )
        ),
    )
)
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


#  compound = assembly.toCompound()
#  exporters.export(compound, "result.glb")
#  exporters.export(assembly.toCompound(), "result.ply")
assembly.save("result.step")
assembly.save("result.gltf")

#  exporters.export(assembly, "result.stl")
