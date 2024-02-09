const gamepadInfo = document.getElementById("gamepad-info");

// window.addEventListener("gamepadconnected", (e) => {
//     const gamepad = navigator.getGampes()[e.gamepad.index];
//     gamepadInfo.textContent = `Gamepad connected at index ${gamepad.index}: ${gamepad.id} It has ${gamepad.buttons.length} buttons and ${gamepad.axes.length} axes.`
// })

window.addEventListener("gamepadconnected", (e) => {
    console.log(
        "Gamepad connected at index %d: %s. %d buttons, %d axes",
        e.gamepad.index,
        e.gamepad.id,
        e.gamepad.buttons.length,
        e.gamepad.axes.length,
    )
})
