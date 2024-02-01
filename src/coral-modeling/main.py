from cadquery import (
    importers,
    Assembly,
    Color,
    Location,
    Vector,
    Workplane,
)


def make_left_pipes(length: float) -> Workplane:
    pvc_radius = 10.766
    # center to center width
    width = 332.111
    # center to center height
    height = 132.165

    #  total_width = 360.0
    total_height = 160.054

    # total height 160.054
    # total width 360.000
    # padding 13.945
    return (
        Workplane("YZ")
        .rect(width, total_height - pvc_radius / 2, forConstruction=True)
        .vertices("<Y and <X")
        .tag("bottom_left")
        .translate(Vector(-length, 0, 0))
        .tag("bottom_back_left")
        .end()
        .end()
        .rect(width, height, forConstruction=True)
        .vertices()
        .circle(pvc_radius)
        .extrude(-length)
    )


def make_right_pipes(length: float) -> Workplane:
    pvc_radius = 10.766
    # center to center width
    width = 332.111
    # center to center height
    height = 290.805

    total_height = 318.694
    # total length 360.000
    return (
        Workplane("YZ")
        .rect(width, total_height - pvc_radius / 2, forConstruction=True)
        .vertices("<Y and <X")
        .tag("bottom_left")
        .translate(Vector(length, 0, 0))
        .tag("bottom_back_left")
        .end()
        .end()
        .rect(width, height, forConstruction=True)
        .vertices()
        .circle(pvc_radius)
        .extrude(length)
    )


def make_top_pipes(height: float) -> Workplane:
    pvc_radius = 10.766
    # center to center length
    length = 346.5
    # center to center width
    width = 332.111

    total_length = 374.389
    #  total_width = 360.000

    return (
        Workplane("XY")
        .rect(
            total_length - pvc_radius / 2,
            width,
            forConstruction=True,
        )
        .vertices(">Y and >X")
        .tag("bottom_anchor_point")
        .translate(Vector(0, 0, height))
        .tag("top_anchor_point")
        .end()
        .end()
        .rect(length, width, forConstruction=True)
        .vertices()
        .circle(12)
        .extrude(height)
    )


def make_coral_restoration_site(
    left_length: float, right_length: float, top_length: float
) -> Assembly:
    # import all the assets
    left_end = importers.importStep("assets/left_end.step")
    right_end = importers.importStep("assets/right_end.step")
    top_end = importers.importStep("assets/top_end_no_coral.step")
    center_box = importers.importStep("assets/center_box.step")
    coral = importers.importStep("assets/coral.step")

    # the variable length pipes that connect the ends to the center box
    left_pipes = make_left_pipes(left_length)
    right_pipes = make_right_pipes(right_length)
    top_pipes = make_top_pipes(top_length)

    return (
        Assembly()
        .add(
            center_box,
            name="center_box",
            loc=Location(Vector(0, 0, 0)),
        )
        .add(left_end, name="left_end")
        .add(right_end, name="right_end")
        .add(left_pipes, name="left_pipes")
        .add(right_pipes, name="right_pipes")
        .add(top_end, name="top_end")
        .add(top_pipes, name="top_pipes")
        .add(
            coral,
            name="coral",
            color=Color(222 / 256, 74 / 256, 124 / 256),
        )
        # the center box shouldn't move
        .constrain("center_box", "Fixed")
        # left end
        # make sure the left end and the left pipes don't rotate
        .constrain("left_end", "FixedRotation", (0, 0, 0))
        .constrain("left_pipes", "FixedRotation", (0, 0, 0))
        # connect the left end to the left pipes
        .constrain(
            "left_end@vertices@>(1, -1, -1)",
            "left_pipes?bottom_back_left",
            "Point",
        )
        # connect the left pipes to the center box
        .constrain(
            "left_pipes?bottom_left",
            "center_box@vertices@>(-1, -1, -1)",
            "Point",
        )
        # right end
        .constrain("right_end", "FixedRotation", (0, 0, 0))
        .constrain("right_pipes", "FixedRotation", (0, 0, 0))
        # connect the right end to the right pipes
        .constrain(
            "right_end@vertices@>(-1, -1, -1)",
            "right_pipes?bottom_back_left",
            "Point",
        )
        # connect the right pipes to the center box
        .constrain(
            "right_pipes?bottom_left",
            "center_box@vertices@>(1, -1, -1)",
            "Point",
        )
        .constrain("right_pipes", "FixedRotation", (0, 0, 0))
        # top end
        .constrain("top_end", "FixedRotation", (0, 0, 0))
        .constrain("top_pipes", "FixedRotation", (0, 0, 0))
        # connect the top end to the top pipes
        .constrain(
            "top_end@vertices@>(1, 1, -1)",
            "top_pipes?top_anchor_point",
            "Point",
        )
        # connect the top pipes to the center box
        .constrain(
            "top_pipes?bottom_anchor_point",
            "center_box@vertices@>(1, 1, 1)",
            "Point",
        )
        .constrain("coral", "FixedRotation", (0, 0, 0))
        # center the coral in the middle of the top end
        .constrain("coral@faces@<Z", "top_end@vertices@>(-1, -1, 1)", "Point")
        .constrain("coral@faces@<Z", "top_end@vertices@>(-1, 1, 1)", "Point")
        .constrain("coral@faces@<Z", "top_end@vertices@>(1, -1, 1)", "Point")
        .constrain("coral@faces@<Z", "top_end@vertices@>(1, 1, 1)", "Point")
        .solve()
    )


def main():
    output_file = "result.glb"
    print("Creating model...")
    coral_restoration_site = make_coral_restoration_site(400, 500, 400)
    coral_restoration_site.save(output_file)
    print(f"Outputted model to {output_file}")


if __name__ == "__main__":
    main()
