<template>
    <transition name="form-fade" mode="out-in" appear>

        <n-grid v-if="showSelectFolderType" :x-gap="8" :y-gap="8" :cols="isMobile() ? 2 : 3">
            <n-grid-item>
                <folder-box @selected="selectFolder" :folder="{}" />
            </n-grid-item>
            <n-grid-item>
                <folder-box @selected="selectFolder" :folder="{}" />
            </n-grid-item>
            <n-grid-item>
                <folder-box @selected="selectFolder" :folder="{}" />
            </n-grid-item>
        </n-grid>

        <div v-else-if="!selectedRule" key="folder-content">
            <n-page-header @back="handleBack">
                <!-- <template #back>
                    <Icon name="ion:arrow-back-outline" />
                </template> -->
                <template #title>
                    <!-- <small style="text-decoration: none; color: inherit"> -->
                    Rotation Folder
                    <!-- </small> -->
                </template>
                <template #avatar>
                    <!-- <n-avatar src="https://cdnimg103.lizhi.fm/user/2017/02/04/2583325032200238082_160x160.jpg" /> -->
                    <folder-icon style="height: 25; width: 25;" :type="TreeFolderType.CapFolder" />
                </template>
            </n-page-header>
            <n-divider>
                <small class="subtitle">CHOOSE RULE</small>
            </n-divider>
            <n-grid :cols="2" :x-gap="8" :y-gap="8">
                <n-grid-item class="folder-select">
                    <n-card hoverable @click="selectRule('country')">
                        <template #default>
                            <n-flex :wrap="false">
                                <n-space>
                                    <n-icon-wrapper :size="27">
                                        <Icon name="ion:earth-outline" />
                                    </n-icon-wrapper>
                                </n-space>
                                <n-space>
                                    <h5>Country</h5>
                                    <span style="font-size: 12px; opacity: 0.6;">
                                        Choose countries to apply the rotation rule
                                    </span>
                                </n-space>
                            </n-flex>

                        </template>
                    </n-card>
                </n-grid-item>
                <n-grid-item class="folder-select">
                    <n-card hoverable>
                        <template #default>
                            <n-flex :wrap="false">
                                <n-space>
                                    <n-icon-wrapper :size="27">
                                        <Icon name="ion:people-outline" />
                                    </n-icon-wrapper>
                                </n-space>
                                <n-space>
                                    <h5>Affiliate</h5>
                                    <!-- Icon Wrapper with Icon -->
                                    <span style="font-size: 12px; opacity: 0.6;">
                                        Choose affiliates to apply the rotation rule
                                    </span>
                                </n-space>
                            </n-flex>

                        </template>
                    </n-card>
                </n-grid-item>
            </n-grid>
        </div>
        <div v-else key="folder-">
            <n-page-header @back="handleBack">
                <!-- <template #back>
                    <Icon name="ion:arrow-back-outline" />
                </template> -->
                <template #title>
                    <!-- <small style="text-decoration: none; color: inherit"> -->

                    <n-grid :cols="24" justify="center" align="start">
                        <n-grid-item :span="10">
                            <n-flex :wrap="false">
                                <n-space>
                                    <!-- <n-icon-wrapper :size="20"> -->
                                    <folder-icon style="height: 20; width: 20;" :type="TreeFolderType.CapFolder" />
                                    <!-- </n-icon-wrapper> -->
                                </n-space>
                                <n-flex>
                                    Rotation Folder
                                    <!-- Icon Wrapper with Icon -->
                                    <span style="font-size: 12px; opacity: 0.6;">
                                        Choose affiliates to apply the rotation rule
                                    </span>
                                </n-flex>
                            </n-flex>
                        </n-grid-item>
                        <n-grid-item :span="4">
                            <n-divider vertical style="height: 20px" />
                        </n-grid-item>

                        <n-grid-item :span="10">
                            <n-flex :wrap="false">
                                <n-space>
                                    <n-icon-wrapper :size="20">
                                        <Icon :size="14" name="ion:people-outline" />
                                    </n-icon-wrapper>
                                </n-space>
                                <n-flex>
                                    Affiliate
                                    <!-- Icon Wrapper with Icon -->
                                    <span style="font-size: 12px; opacity: 0.6;">
                                        Choose affiliates to apply the rotation rule
                                    </span>
                                </n-flex>
                            </n-flex>
                        </n-grid-item>

                    </n-grid>
                    <!-- </div> -->

                    <!-- </small> -->
                </template>
            </n-page-header>
            <n-divider>
                <small class="subtitle">CHOOSE RULE</small>
            </n-divider>
            <n-form :cols="2" :x-gap="8" :y-gap="8">
                <n-form-item label="Name">
                    <n-input placeholder="Folder Name" />
                </n-form-item>
                <n-form-item label="Description">
                    <n-input placeholder="Folder Description" />
                </n-form-item>
                <n-form-item label="Affiliate">
                    <n-select :options="options" placeholder="Select Option" />
                </n-form-item>

                <!-- <n-form-item :show-label="false"> -->
                <n-flex justify="flex-end">
                    <n-button secondary type="primary">Cancel</n-button>
                    <n-button type="primary">
                        Create
                    </n-button>
                </n-flex>
                <!-- </n-form-item> -->

            </n-form>
        </div>
    </transition>
</template>


<script setup lang="ts">
import { defineComponent, ref } from 'vue'
import { isMobile } from '@/utils'
import type { BaseFolder } from '@/types/tree'
import FolderBox from '@/components/Tree/FolderBox.vue'
import { NIconWrapper, NGrid, NGridItem, NPageHeader, NForm, NFormItem, NSelect, NInput, NSpace, NFlex, NCard, NDivider, NButton } from 'naive-ui'
import FolderIcon from './FolderIcon.vue'
import { TreeFolderType } from '@/types/tree'
import Icon from '@/components/common/Icon.vue'
const handleBack = () => {
    showSelectFolderType.value = true
}
const options = ref([
    { label: 'Option 1', value: '1' },
    { label: 'Option 2', value: '2' },
    { label: 'Option 3', value: '3' },
])
const showSelectFolderType = ref(true)
const selectedRule = ref('')

const selectFolder = (folder: BaseFolder) => {
    showSelectFolderType.value = false
}

const selectRule = (rule: string) => {
    selectedRule.value = rule
}

</script>


<style lang="scss" scoped>
.subtitle {
    line-height: 1.2;
    font-size: 10px;
    opacity: 0.4;
    font-weight: 500;
    font-family: var(--font-family);
}

.folder-select {
    .n-card {
        cursor: pointer;
    }
}


.form-fade-enter-active,
.form-fade-leave-active {
    transition:
        opacity 0.2s,
        transform 0.2s;
}

.form-fade-enter-from {
    opacity: 0;
    transform: translateX(10px);
}

.form-fade-leave-to {
    opacity: 0;
    transform: translateX(-10px);
}
</style>