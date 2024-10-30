<template>
    <n-card :class="{ 'folder-selected': isSelected, 'folder-box': true }">
        <button @click="handleClick" text>
            <div class="folder-content">
                <FolderIcon :size="30" :type="TreeFolderType.RotationContolAffiliateFolder" />
                <TargetFolderIcon :size="30" :type="TreeFolderType.RotationControlAdvertiserFolder" />
                <!-- <Icon name="carbon:folder" :size="45" /> -->
                <div class="folder-info">
                    <div class="folder-name">Split Folder</div>
                </div>
                <!-- subtitle -->
                <div class="folder-metadata">
                    <span>Create split folder</span>
                </div>
            </div>
        </button>
    </n-card>
</template>
  
  
<script setup lang="ts">
import { toRefs, ref } from 'vue';
import { NCard, NButton } from 'naive-ui';
import Folder from '@/components/Tree/Folder.vue';
import FolderIcon from '@/components/Tree/FolderIcon.vue';
import TargetFolderIcon from './TargetFolderIcon.vue';
import Icon from '@/components/common/Icon.vue';
import { TreeFolderType, type TreeFolder } from '@/types/tree';
const isSelected = ref(false);

const props = defineProps({
    folder: {
        type: Object,
        required: true
    }
});

const { folder } = toRefs(props);

const emit = defineEmits(['selected']);
// emit @selected event
const handleClick = () => {
    isSelected.value = !isSelected.value;
    emit('selected', folder);
};


</script>
<style scoped lang="scss">
.folder-box {
    width: 100%;
    /* Adjust this as needed for your layout */
    position: relative;

    /* set max height and width */
    max-width: 150px;
    max-height: 150px;
}

// set properties for hover selected folder box

.folder-box::before {
    content: "";
    display: block;
    padding-top: 100%;
    /* Aspect ratio 1:1 */
}

.folder-content {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    text-align: center;
}

.folder-info {
    margin-top: 10px;
}

.folder-name {
    font-weight: 400;
    font-size: 14px;
}

.folder-metadata span {
    display: block;
    font-size: 12px;
    color: #666;
}

.folder-selected {
    // background-color: #ffffff56;
    border: 1px solid #ebebeb29;
    // fill like the box is selected 

    // .folder-content {
    //     background-color: #f5f5f5;
    // }

}



.n-card {

    transition: all 0.2s ease-in-out;
    cursor: pointer;

    &:hover {
        box-shadow: 0px 0px 10px 3px rgba(0, 0, 0, 0.07);
        // position up a bit 
        transform: translateY(-5px);
    }

    &:hover .folder-selected {
        box-shadow: unset;
        // position up a bit
        transform: unset;
    }

}
</style>