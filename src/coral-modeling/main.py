#!.venv/bin/python
from cadquery import (
    importers,
    Assembly,
    Color,
    Location,
    Vector,
    Workplane,
)


from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs


def make_left_pipes(length: float) -> Workplane:
    pvc_radius = 10.766
    # center to center width
    width = 332.111
    # center to center height
    height = 132.165

    total_height = 160.054

    # total height 160.054
    # total width 360.000
    padding = 13.945
    return (
        Workplane("YZ")
        .rect(
            width,
            total_height - pvc_radius / 2,
            forConstruction=True,
        )
        .vertices("<YZ")
        .tag("bottom_left")
        .end()
        .vertices(">YZ")
        .translate(Vector(-length, padding, -pvc_radius))
        .tag("end_anchor_point")
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
        .vertices("<YZ")
        .tag("center_box_anchor_point")
        .end()
        .vertices(">YZ")
        .translate(Vector(length, 0, pvc_radius / 4))
        .tag("end_anchor_point")
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
        .circle(pvc_radius)
        .extrude(height)
    )


def make_left_platform(pipe_length: float) -> Workplane:
    # need to add an additional 58mm to take into account the length of the
    # tee and elbow
    length = pipe_length + 58
    width = 360
    height = 8
    return Workplane("XY").rect(length, width).extrude(height)


def make_right_platform(pipe_length: float) -> Workplane:
    # need to add an additional 58mm to take into account the length of the
    # tee and elbow
    length = pipe_length + 58
    width = 360
    height = 8
    return Workplane("XY").rect(length, width).extrude(height)


def make_velcro_square() -> Workplane:
    length = 150
    width = 150
    height = 2
    return Workplane("XY").box(length, width, height)


def make_coral_restoration_site(
    left_length: float,
    right_length: float,
    top_length: float,
) -> Assembly:
    # import all the assets
    left_end = importers.importStep("assets/left_end.step")
    right_end = importers.importStep("assets/right_end.step")
    top_end = importers.importStep("assets/top_end_no_coral.step")
    center_box = importers.importStep("assets/center_box.step")
    coral = importers.importStep("assets/coral.step")
    left_thingy = importers.importStep("assets/left_thingy.step")

    # the variable length pipes that connect the ends to the center box
    left_pipes = make_left_pipes(left_length)
    right_pipes = make_right_pipes(right_length)
    top_pipes = make_top_pipes(top_length)

    # the platforms that sit on top of the sides
    left_platform = make_left_platform(left_length)
    right_platform = make_right_platform(right_length)

    # the red velcro square where the brain coral is placed
    velcro_square = make_velcro_square()

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
        .add(left_platform, name="left_platform")
        .add(right_platform, name="right_platform")
        .add(velcro_square, name="velcro_square", color=Color("red"))
        .add(
            coral,
            name="coral",
            color=Color(222 / 256, 74 / 256, 124 / 256),
        )
        .add(left_thingy, name="left_thingy")
        # the center box shouldn't move
        .constrain("center_box", "Fixed")
        # left end
        # make sure the left end and the left pipes don't rotate
        .constrain("left_end", "FixedRotation", (0, 0, 0))
        .constrain("left_pipes", "FixedRotation", (0, 0, 0))
        # connect the left end to the left pipes
        .constrain(
            "left_end@vertices@>(1, 1, 1)",
            "left_pipes?end_anchor_point",
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
            "right_end@vertices@>(-1, 1, 1)",
            "right_pipes?end_anchor_point",
            "Point",
        )
        # connect the right pipes to the center box
        .constrain(
            "right_pipes?center_box_anchor_point",
            "center_box@vertices@>(1, -1, -1)",
            "Point",
        )
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
        # place the left platform on top of the left end and pipes
        .constrain("left_platform", "FixedRotation", (0, 0, 0))
        .constrain(
            "left_platform@vertices@>(-1, -1, -1)",
            "left_end@vertices@>(-1, -1, 1)",
            "Point",
        )
        .constrain(
            "left_platform@vertices@>(-1, 1, -1)",
            "left_end@vertices@>(-1, 1, 1)",
            "Point",
        )
        # place the right platform on top of the right end and pipes
        .constrain("right_platform", "FixedRotation", (0, 0, 0))
        .constrain(
            "right_platform@vertices@>(1, -1, -1)",
            "right_end@vertices@>(1, -1, 1)",
            "Point",
        )
        .constrain(
            "right_platform@vertices@>(1, 1, -1)",
            "right_end@vertices@>(1, 1, 1)",
            "Point",
        )
        # place the velcro square in the middle of the right platform
        .constrain(
            "velcro_square@vertices@>(-1, -1, -1)",
            "right_platform@vertices@>(-1, -1, 1)",
            "Point",
        )
        .constrain(
            "velcro_square@vertices@>(-1, 1, -1)",
            "right_platform@vertices@>(-1, 1, 1)",
            "Point",
        )
        .constrain(
            "velcro_square@vertices@>(1, -1, -1)",
            "right_platform@vertices@>(1, -1, 1)",
            "Point",
        )
        .constrain(
            "velcro_square@vertices@>(1, 1, -1)",
            "right_platform@vertices@>(1, 1, 1)",
            "Point",
        )
        # the velcro square should be a little offset towards the right
        .constrain(
            "velcro_square@vertices@>(1, -1, -1)",
            "right_platform@vertices@>(1, -1, 1)",
            "Point",
        )
        .constrain(
            "velcro_square@vertices@>(1, 1, -1)",
            "right_platform@vertices@>(1, 1, 1)",
            "Point",
        )
        # center the coral in the middle of the top end
        .constrain("coral", "FixedRotation", (0, 0, 0))
        .constrain("coral@faces@<Z", "top_end@vertices@>(-1, -1, 1)", "Point")
        .constrain("coral@faces@<Z", "top_end@vertices@>(-1, 1, 1)", "Point")
        .constrain("coral@faces@<Z", "top_end@vertices@>(1, -1, 1)", "Point")
        .constrain("coral@faces@<Z", "top_end@vertices@>(1, 1, 1)", "Point")
        # place the left thingy on top of the left end
        .constrain("left_thingy", "FixedRotation", (0, 0, 0))
        .constrain(
            "left_thingy@faces@<Z",
            "left_platform@vertices@>(-1, -1, 1)",
            "Point",
        )
        .constrain(
            "left_thingy@faces@<Z",
            "left_platform@vertices@>(-1, 1, 1)",
            "Point",
        )
        .solve()
    )


def create_file():
    output_file = "result.glb"
    print("Creating model...")
    coral_restoration_site = make_coral_restoration_site(400, 500, 400)
    coral_restoration_site.save(output_file)
    print(f"Outputted model to {output_file}")


class ReqHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = parse_qs(self.path)
        print(parsed_url)
        left = int(parsed_url['/left'][0])
        right = int(parsed_url['right'][0])
        top = int(parsed_url['top'][0])


        output_file = "../frontend/public/result.glb"
        print("Creating model...")
        coral_restoration_site = make_coral_restoration_site(left, right, top)
        coral_restoration_site.save(output_file)
        print(f"Outputted model to {output_file}")
        self.send_response(200)
    
    def end_headers(self) -> None:
        self.send_header('Access-Control-Allow-Origin', '*')

if __name__ == "__main__":
    print("hello")
    addr = ("127.0.0.1", 3000)
    httpd = HTTPServer(addr, ReqHandler)
    httpd.serve_forever()


