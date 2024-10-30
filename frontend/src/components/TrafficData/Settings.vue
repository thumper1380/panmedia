<template>
    <n-drawer resizable :default-width="drawerWidth" placement="right">
        <n-drawer-content closable>
            <template #header>
                <n-flex align="center" justify="center">
                    <Icon name="ion:settings-outline" :size="20" />
                    Settings
                </n-flex>
            </template>
            <template #default>
                <n-scrollbar>
                    <n-form>
                        <draggable :animation="100" :list="localColumnsConfig" group="column-settings" item-key="key"
                            class="drag-area">
                            <template #item="{ element: column }">
                                <div class="column-setting" size="small">
                                    <!-- add dragging icon -->
                                    <n-flex class="drag-area" justify="space-between" align="center">
                                        <Icon name="ion:reorder-three-outline" :size="20" />
                                        <span>{{ column.title }}</span>
                                    </n-flex>
                                    <n-switch :key="column.key" v-model:value="column.visible" />
                                    <!-- {{ column.visible }} -->
                                </div>
                            </template>
                        </draggable>

                        <!-- set table items per page using n-select with options: 10, 20, 50, 100 -->

                    </n-form>
                </n-scrollbar>
            </template>
            <template #footer>
                <n-flex>
                    <!-- reset -->
                    <n-popconfirm>
                        <template #trigger>
                            <n-button>Reset</n-button>

                        </template>
                        Are you sure you want
                        <br />
                        to reset the settings?
                    </n-popconfirm>


                    <n-button type="primary" @click="saveSettings">Save</n-button>
                </n-flex>
            </template>
        </n-drawer-content>
    </n-drawer>
</template>

  
<script setup lang="ts">
import { watch, toRefs, ref, type PropType, computed, onMounted } from 'vue';
import { NDrawer, NDrawerContent, NSwitch, NForm, NPopconfirm, NScrollbar, NFlex, NButton, NFormItem, NSelect } from 'naive-ui';
import draggable from 'vuedraggable';
import { isMobile } from '@/utils';
import Icon from '@/components/common/Icon.vue';
const drawerWidth = ref(isMobile() ? '100%' : '350px');






type ColumnConfig = {
    key: string;
    title: string;
    type: string;
    minWidth: number;
    maxWidth: number;
    width: number;
    resizable: boolean;
    visible: boolean;
};

const props = defineProps({
    columnsConfig: {
        type: Array as PropType<ColumnConfig[]>,
        required: true,
    },
});


// use local reactive state for columnsConfig
const { columnsConfig } = toRefs(props);


const localColumnsConfig = ref([]);

watch(columnsConfig, (newVal) => {
    localColumnsConfig.value = JSON.parse(JSON.stringify(newVal));
}, { deep: true, immediate: true });



const checkMove = (evt: any) => {
    // Prevent dragging the first item
    console.log(evt);
};




onMounted(() => {
});


const emit = defineEmits(['update:columnsConfig'])

const saveSettings = () => {
    // Emit the updated configuration
    emit('update:columnsConfig', localColumnsConfig.value);
};

</script>

<style scoped>
.column-setting {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 10px;
    padding: 5px 0;
    padding-right: 20px;
}

.column-setting::last-child {
    margin-bottom: 0;
}

.column-setting span {
    font-size: 14px;
    font-weight: 500;
}

.drag-area {
    cursor: move;
    /* cant be selecterd */
    user-select: none;
}
</style>