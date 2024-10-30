<template>
    <n-card>
        
    </n-card>
</template>


<script setup lang="ts">
import { NCard, NDescriptions, NDescriptionsItem, NTag, NIconWrapper, NIcon, NEllipsis } from 'naive-ui'
import { h, toRefs } from 'vue'
import Icon from '@/components/common/Icon.vue'
import ModelDetial from '@/components/common/Model/ModelDetailView.vue';


const props = defineProps({
    detail: {
        type: Object,
        required: true
    }
})
const { detail } = toRefs(props)

const formatText = (text: string) => {
    if (!text) return '';
    return text
        .toLowerCase()
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');

}
</script>
<style lang="scss" scoped></style>