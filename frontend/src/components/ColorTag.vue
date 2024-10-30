<template>
    <n-tag :color="{ color: backgroundColor, borderColor: borderColor, textColor: textColor }">{{ text }}</n-tag>
</template>



<script setup lang="ts" >
import { toRefs, ref, h, computed } from 'vue';
import { NTag } from 'naive-ui';
import { colord } from 'colord';


const props = defineProps({
    color: {
        type: String,
        default: '#000'
    },
    text: {
        type: String,
    },
});

const { color, text } = toRefs(props);

const backgroundColor = computed(() => {
    // if it's dark, lighten it
    return colord(color.value).lighten(0.09).toHex();
});


// computed border color
const borderColor = computed(() => {
    return colord(color.value).darken(0.00001).toHex();
});

// computed text color
const textColor = computed(() => {
    const c = colord(color.value).lighten(0.09)
    return c.isDark() ? '#eee' : '#000';
});

</script>

<style lang="scss" scoped>
.n-tag {}
</style>