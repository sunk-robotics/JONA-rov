import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import CameraView from "../views/CameraView.vue"
import CoralView from "../views/CoralView.vue"
import MeasureView from "../views/MeasureView.vue"

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: "/cameras",
      name: "camera",
      component: CameraView
    },
    {
      path: "/coral",
      name: "coral",
      component: CoralView
    },
    {
      path: "/measure",
      name: "measure",
      component: MeasureView
    }
  ]
})

export default router
