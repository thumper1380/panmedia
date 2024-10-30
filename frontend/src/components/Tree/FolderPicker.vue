<template>
    <div class="folder-picker">
        <FolderBox v-for="folder in folders" :key="folder.name" :folder="folder" :selected="selectedFolder === folder"
            @click="selectFolder(folder)" />
    </div>
</template>
  
<script setup lang="ts">
import { ref } from 'vue';
import FolderBox from './FolderBox.vue';

type Folder = {
    name: string;
    id: number;
    // Add other properties as needed
};


const folders = ref<Folder[]>(/* Array of folders */);
const selectedFolder = ref<Folder | null>(null);

function selectFolder(folder: Folder) {
    selectedFolder.value = folder;
    // Emit an event or handle the selection as needed
}
</script>
  
<style scoped>
.folder-picker {
    /* Your styles here */
}
</style>
  