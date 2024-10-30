<template>
    <svg aria-hidden="true" focusable="false" role="img" class="icon-directory" viewBox="0 0 16 16" :width="size"
        :height="size" style="display: inline-block; user-select: none; vertical-align: text-bottom; overflow: visible;">
        <path
            d="M1.75 1A1.75 1.75 0 0 0 0 2.75v10.5C0 14.216.784 15 1.75 15h12.5A1.75 1.75 0 0 0 16 13.25v-8.5A1.75 1.75 0 0 0 14.25 3H7.5a.25.25 0 0 1-.2-.1l-.9-1.2C6.07 1.26 5.55 1 5 1H1.75Z">
        </path>
    </svg>
    <!-- <svg :fill="color" aria-hidden="true" focusable="false" role="img" class="circle-icon" viewBox="0 0 16 16" width="16"
        height="16" style="display: inline-block; user-select: none; vertical-align: text-bottom; overflow: visible;">
        <circle cx="8" cy="8" r="7" />
    </svg>
     -->
</template>
  
<script setup lang="ts">
import { toRefs, computed, ref } from 'vue'
import { TreeFolderType } from '@/types/tree'

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

// add color and text to toRefs
const { type } = toRefs(props)


// #00B27B - green
// #6267FF - blue
// #FF61C9 - pink
// #FFB600 - yellow
// #FF0156 - red

const color = computed(() => {
    switch (type.value) {
        case TreeFolderType.RotationControlCountryFolder:
            return '#FFB600'
        case TreeFolderType.RotationContolAffiliateFolder:
            return '#FFB600'
        case TreeFolderType.RotationControlAdvertiserFolder:
            return '#FFB600'

        case TreeFolderType.RotationControlCountrySplitFolder:
            return '#FF61C9'
        case TreeFolderType.RotationControlAdvertiserSplit:
            return '#FFB600'

        case 'CapFolder':
            return '#00B27B'
    }
})

const letter = ref('A')



</script>
  
<style lang="scss" scoped>
.icon-directory {
    fill: v-bind(color);
}

.letter {
    font-size: 0.5em;
    font-weight: 600;
    color: #fff;
    position: absolute;
    top: 50%;
    left: 20%;
    transform: translate(-50%, -50%);
}
</style>
  