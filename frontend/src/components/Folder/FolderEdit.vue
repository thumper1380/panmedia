<template>
    <div class="folder-edit-view">
        <n-card title="Edit Folder" embedded class="edit-card">
            <template #header-extra>
                <n-switch v-model:value="folderStatus" />
            </template>
            <template #default>
                {{ folder.type }}
                <n-form :label-placement="isMobile() ? 'top' : 'top'" class="edit-form">
                    <n-form-item class="fade-in" label="Folder Name">
                        <n-input v-model:value="folder.name" />
                    </n-form-item>
                    <n-form-item label="Affiliate">
                        <n-select :options="folderTypes" />
                        
                    </n-form-item>
                    
                    <n-form-item>
                        
                        <n-button type="primary" @click="show = !show">
                            <Icon name="carbon:add" :size="20" v-if="!show" />
                            <Icon name="carbon:subtract" :size="20" v-if="show" />
                            <span class="ml-2">
                                Add Cap Folder
                            </span>
                        </n-button>
                    </n-form-item>
                    <n-collapse-transition :show="show">
                        <!-- <n-input v-model:value="folder.name" />
                            </n-form-item> -->
                        <!-- slider to select cap, 0 - 1000 -->
                        <n-form-item label="Daily Cap" class="mt-7 mb-0">
                            <n-slider :min="0" :max="1000" :step="10" style="width: 200px" />
                        </n-form-item>

                    </n-collapse-transition>

                </n-form>
            </template>

            <template #footer>
                <n-button type="primary" @click="editFolder">Save</n-button>
            </template>

        </n-card>
    </div>
</template>

<script setup lang="ts">
import { toRefs, ref, computed } from 'vue'
import { NForm, NFormItem, NInput, NButton, NCard, NSelect, NSwitch, NCollapseTransition, NSlider, NInputGroup } from 'naive-ui'
import { isMobile } from '@/utils'
import Icon from '@/components/common/Icon.vue'
import type { TreeFolder } from '@/types/tree'




const props = defineProps({
    folder: {
        type: Object as () => TreeFolder,
        required: true
    }
})

const { folder } = toRefs(props)

const folderStatus = ref(!folder.value.disabled)

const show = ref(false)




const folderTypes = ref([
    { label: 'Affiliate 1', value: 'affiliate_1' },
    // create 2 more 
    { label: 'Affiliate 2', value: 'affiliate_2' },
    { label: 'Affiliate 3', value: 'affiliate_3' }
])

const editFolder = () => {
    console.log(props.folder)
}
</script>


<style lang="scss" scoped>
.folder-edit-view {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    animation: folder-view 0.3s ease-in-out forwards;


    .edit-card {
        min-height: 100%;
    }

    @keyframes folder-view {
        from {
            transform: translateY(-10%);
            opacity: 0;
        }

        to {
            transform: translateY(0);
            opacity: 1;
        }
    }


}
</style>