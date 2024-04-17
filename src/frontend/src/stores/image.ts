import { defineStore } from "pinia";
import { ref } from "vue";

export const useImageStore = defineStore('image', () => {
    const image = ref<VideoFrame | null>(null)

    function set(buf: VideoFrame) {
        image.value = buf
    }

    function get(): VideoFrame {
        return image.value
    }

    function clear(): void { 
        image.value = null;
    }

    return { image, set, get }
})

export const useCounterStore = defineStore('counter', () => {
    let count = 0

    function incr() {
        count++
    }

    return { count, incr }
})
