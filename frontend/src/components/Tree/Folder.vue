<template>
    <div class="folder-icon" :style="folderStyle">
        <div class="folder-tab"></div>
        <span class="folder-content">{{ content }}</span>
    </div>
</template>
  
<script setup>
import { computed } from 'vue';

const props = defineProps({
    color: {
        type: String,
        default: '#d11e5b'
    },
    content: {
        type: String,
        default: 'CAP'
    },
    size: {
        type: Number,
        default: 20 // default size, you can adjust as needed
    }
});

const lightenColor = (color, percent) => {
    const num = parseInt(color.replace("#", ""), 16),
        amt = Math.round(2.55 * percent),
        R = (num >> 16) + amt,
        B = (num >> 8 & 0x00FF) + amt,
        G = (num & 0x0000FF) + amt;
    return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 + (B < 255 ? B < 1 ? 0 : B : 255) * 0x100 + (G < 255 ? G < 1 ? 0 : G : 255)).toString(16).slice(1);
};


const folderStyle = computed(() => {
    const gradientEndColor = lightenColor(props.color, 15); // Lighten by 30%
    const scale = props.size / 50; // Assuming 50 is the original size for width and height

    return {
        '--folder-color': props.color,
        '--folder-gradient-end': gradientEndColor,
        '--folder-tab-width': `${scale * 20}px`, // Adjust width of the tab
        '--folder-tab-height': `${scale * 5}px`, // Adjust height of the tab
        '--folder-tab-right': `${scale * -5}px`, // Adjust right position of the tab cut
        '--folder-tab-border': `${scale * 5}px`, // Adjust size of the tab cut
        '--folder-content-font-size': `${scale * 1.2}rem`, // Adjust font size of content
        background: `linear-gradient(-45deg, var(--folder-color) 0%, var(--folder-gradient-end) 100%)`,
        width: `${props.size - 2}px`,
        height: `${(props.size * 35) / 50}px`, // Maintain the aspect ratio based on the original size
    };
});
</script>
  
<style scoped lang="scss">
.folder-icon {
    position: relative;
    border-top-right-radius: 2px;
    border-bottom-right-radius: 2px;
    border-bottom-left-radius: 2px;
    margin: 0;
    // box-shadow: 0px 1px 5px rgba(0, 0, 0, 0.1);
}

.folder-tab {
    position: absolute;
    top: -0.125rem;
    left: 0;
    width: var(--folder-tab-width);
    height: var(--folder-tab-height);
    border-top-left-radius: 4px;
    background-color: var(--folder-color);
}

.folder-tab::before {
    content: "";
    position: absolute;
    right: -0.11rem;
    top: 0px;
    border-top: var(--folder-tab-border) solid var(--folder-color);
    border-left: var(--folder-tab-border) solid transparent;
    box-shadow: 3px -1px 3px rgba(0, 0, 0, 0.1);
    transform: rotate(180deg);
}

.folder-content {
    position: absolute;
    left: 50%;
    top: 55%;
    transform: translate(-50%, -50%);
    color: #ffffff;
    font-weight: 600;
    font-size: .6rem;
    user-select: none;
    font-family: 'Roboto', sans-serif;
}
</style>
  