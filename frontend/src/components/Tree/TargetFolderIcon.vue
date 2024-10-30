<template>
    <div class="icon-with-text">
        <n-avatar lazy :size="size" :round="true" :color="color">
            {{ text }}
        </n-avatar>
    </div>
</template>

<script setup lang="ts">
import { toRefs, computed } from 'vue'
import type { TreeFolderType } from '@/types/tree'
import { NAvatar } from 'naive-ui';

// add color and text props
const props = defineProps({
    type: {
        type: String as () => TreeFolderType,
        required: true
    },
    size: {
        type: Number,
        default: 16
    }
})

// compute text according to size
const textSize = computed(() => {
    switch (props.size) {
        case 16:
            return '8px'
        case 20:
            return '10px'
        case 24:
            return '16px'
        case 30:
            return '18px'
        case 36:
            return '20px'
        case 40:
            return '22px'
        case 48:
            return '24px'
    }
})

// add color and text to toRefs
const { type } = toRefs(props)

const color = computed(() => {
    switch (type.value) {
        case 'CapFolder':
            return '#00B27B'
        case 'RotationControlAdvertiserFolder':
            return '#6267FF'
        case 'RotationControlAdvertiserSplit':
            return '#6267FF'
    }
})

const text = computed(() => {
    switch (type.value) {
        case 'CapFolder':
            return 'C'
        case 'RotationControlAdvertiserFolder':
            return 'A'
        case 'RotationControlAdvertiserSplit':
            return 'A'
    }
})
</script>

<style lang="scss" scoped>
.icon-with-text {
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.circle-container {
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    /* Makes the div a circle */
    overflow: hidden;
    line-height: 0;
}

.icon-text {
    font-weight: 600;
    color: white;
    user-select: none;
}
</style>
