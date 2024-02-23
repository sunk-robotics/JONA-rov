const GAMEPAD_WS_URL = "ws://192.168.0.102:8765";
const GAMEPAD_CLIENT_INFO = {client_type: "joystick"};
let gamepad_ws: WebSocket;

type Buttons = {
    north?: boolean,
    east?: boolean,
    south?: boolean,
    west?: boolean,

    left_bumper?: boolean,
    right_bumper?: boolean,
    left_trigger?: boolean,
    right_trigger?: boolean,

    select?: boolean,
    start?: boolean,
    mode?: boolean,

    left_thumb?: boolean,
    right_thumb?: boolean
}

function getButtons(gamepad: Gamepad): Buttons {
  let buttons: Buttons = {}
  
  buttons.north = gamepad.buttons[3].pressed;
  buttons.east = gamepad.buttons[1].pressed;
  buttons.south = gamepad.buttons[0].pressed;
  buttons.west = gamepad.buttons[2].pressed;

  buttons.left_bumper = gamepad.buttons[4].pressed;
  buttons.right_bumper = gamepad.buttons[5].pressed;
  buttons.left_trigger = gamepad.buttons[6].pressed;
  buttons.right_trigger = gamepad.buttons[7].pressed;

  buttons.select = gamepad.buttons[8].pressed;
  buttons.start = gamepad.buttons[9].pressed;
  buttons.mode = gamepad.buttons[16].pressed;
  
  buttons.left_thumb = gamepad.buttons[10].pressed;
  buttons.right_thumb = gamepad.buttons[11].pressed;

  return buttons;
}

function getDpad(gamepad: Gamepad): number[] {
  let dpad_x = gamepad.buttons[15].value - gamepad.buttons[14].value;
  let dpad_y = gamepad.buttons[12].value - gamepad.buttons[13].value;
  return [dpad_x, dpad_y];
}

function getLeftStick(gamepad: Gamepad): number[] {
  let x_axis = filterAxis(gamepad.axes[0]);
  let y_axis = -filterAxis(gamepad.axes[1]);
  return [x_axis, y_axis];
}

function getRightStick(gamepad: Gamepad): number[] {
  let x_axis = filterAxis(gamepad.axes[2]);
  let y_axis = -filterAxis(gamepad.axes[3]);
  return [x_axis, y_axis];
}

function filterAxis(axis_value: number): number {
  const deadzone = 0.1;
  if (Math.abs(axis_value) < deadzone) {
    return 0.0;
  } else {
    return axis_value;
  }
}



function connectGamepadWebsocket() {
  if (gamepad_ws != null && gamepad_ws.readyState == 3) {
    gamepad_ws = new WebSocket(GAMEPAD_WS_URL);
    gamepad_ws.addEventListener("open", (event) => {
      gamepad_ws.send(JSON.stringify(GAMEPAD_CLIENT_INFO));
      console.log("Gamepad websocket connected!");
    });
  }
}


function mainLoop() {
  const gamepad = navigator.getGamepads()[0];
  if (gamepad == null || gamepad_ws == null || gamepad_ws.readyState != 1) {
    return;
  }


  const gamepad_data = {
    "buttons": getButtons(gamepad),
    "left_stick": getLeftStick(gamepad),
    "right_stick": getRightStick(gamepad),
    "dpad": getDpad(gamepad),
  };

  gamepad_ws.send(JSON.stringify(gamepad_data));
}

function main() {
  console.log("hello world!");
  gamepad_ws = new WebSocket(GAMEPAD_WS_URL);
  gamepad_ws.addEventListener("open", (event: Event) => {
    gamepad_ws.send(JSON.stringify(GAMEPAD_CLIENT_INFO));
    console.log("Gamepad websocket connected!");
  });

  window.addEventListener("gamepadconnected", (e) => {
    console.log(
      "Gamepad connected at index %d: %s. %d buttons, %d axes",
      e.gamepad.index,
      e.gamepad.id,
      e.gamepad.buttons.length,
      e.gamepad.axes.length,
    )
  })

  window.addEventListener("gamepaddisconnected", (e) => {
    console.log("Gamepad disconnected!");
  })


  setInterval(connectGamepadWebsocket, 100);
  setInterval(mainLoop, 1);
}

export { main, gamepad_ws }
