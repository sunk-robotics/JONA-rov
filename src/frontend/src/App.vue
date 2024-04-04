<script setup lang="ts">
  import { RouterView } from 'vue-router';
  import { gamepad_ws, main } from './scripts/gamepad';
  gamepad_ws;

  main()
</script>

<template>
    <RouterView></RouterView>
</template>

<style>
  body {
    padding: 0;
    margin: 0;
    max-height: 45vh;
    height: 45vh;
    background-color: black;
  }
</style>
