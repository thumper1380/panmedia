<template>
    <div class="page list-view">
        <n-spin :show="showSpin" class="h-full">
            <n-card size="medium">
                <template #header>
                    <!-- back button -->
                    Affiliates
                </template>
                <template #header-extra>
                    <div class="table-toolbar">
                        <n-flex>
                            <n-button :focusable="false" text size="small" class="plus-icon"
                                @click="() => showAddDrawer = true" v-if="canCreate">
                                <Icon name="ion:add" :size="20" />
                            </n-button>
                            <!-- <n-dropdown v-if="!isMobile()" :options="dropDownOptions" @select="handleDropDownselect"
                                trigger="click" placement="bottom-end">
                                <n-button :focusable="false" text size="small">
                                    <Icon name="carbon:overflow-menu-vertical" :size="20" />
                                </n-button>
                            </n-dropdown>
                            <n-button :focusable="false" text size="small" @click="getAffiliates">
                                <Icon name="tabler:refresh" :size="20" />
                            </n-button> -->
                        </n-flex>

                    </div>
                </template>
                <ModelAdd :schema="schema" :show-drawer="showAddDrawer" @update:show-drawer="showAddDrawer = $event"
                    @submit="onCreate" :loading="loading" />

                <ModelEdit :schema="schema" :show-drawer="showEditDrawer" :entity-data="selectedRow"
                    @update:show-drawer="showEditDrawer = $event" @submit="onUpdate" :loading="loading" />


                <n-data-table :row-props="rowProps" striped :scroll-x="1400" :data="affiliates" :columns="columns">
                </n-data-table>
                <n-dropdown :animated="true" :on-select="handleContextMenuSelect"
                    :on-clickoutside="() => showContextMenu = false" placement="bottom-start" trigger="manual" :x="x" :y="y"
                    :options="contextMenuOptions" :show="showContextMenu">
                </n-dropdown>
                <n-flex :justify="isMobile() ? 'center' : 'flex-end'" :class="isMobile() ? 'mt-5' : 'mt-5'">
                    <n-pagination :total="affiliates.length" v-model:page="page" :page-size="5" />
                </n-flex>
            </n-card>
        </n-spin>
    </div>
</template>
<script setup lang="ts">
import { toRefs, ref, h, onMounted, computed } from 'vue';
import { NDropdown, NButton, NCard, NDataTable, NPagination, NSpin, NFlex, useDialog } from 'naive-ui';
import Icon from '@/components/common/Icon.vue';
import { RouterLink } from 'vue-router';
import { list, create, disable, enable, update } from '@/services/affiliateService';
import type { DataTableColumns } from 'naive-ui';
import type { Affiliate, AffiliateCreate } from '@/types/affiliate';
import ModelAdd from '@/components/common/Model/ModelAdd.vue';
import ModelEdit from '@/components/common/Model/ModelEdit.vue';
import { isMobile } from '@/utils';
import renderColumn from '@/utils/table';


const props = defineProps({
    permissions: {
        type: Array as () => string[],
        default: () => ['affiliate.view', 'affiliate.credate', 'affiliate.update', 'affiliate.delete']
    }
});


const { permissions } = toRefs(props);

const canCreate = computed(() => true);
const canUpdate = computed(() => permissions.value.includes('affiliate.update'));
const canDelete = computed(() => permissions.value.includes('affiliate.delete'));
const canView = computed(() => permissions.value.includes('affiliate.view'));





const selectedRow = ref<Affiliate | null>(null);

const rowProps = (row: Affiliate) => {
    return {
        onContextmenu: (e: MouseEvent) => {
            e.preventDefault();
            x.value = e.clientX;
            y.value = e.clientY;
            selectedRow.value = row;
            showContextMenu.value = true;
        }
    };
};




const columns = computed(() => {
    return schema.value.map((field: any) => {
        return {
            title: field.title,
            key: field.key,
            render: (row: any) => renderColumn('AffiliateDetails', row, field)
        };
    });
});

const contextMenuOptions = computed(() => {
    return [
        {
            label: 'Edit',
            key: 'editAffiliate',
            icon: () => h(Icon, { name: 'carbon:edit' }),
        },
        {
            label: selectedRow.value?.is_active ? 'Disable' : 'Enable',
            key: selectedRow.value?.is_active ? 'disableAffiliate' : 'enableAffiliate',
            icon: () => h(Icon, { name: selectedRow.value?.is_active ? 'carbon:close' : 'carbon:checkmark' }),
        },
    ];
});


const showContextMenu = ref(false);
const x = ref(0);
const y = ref(0);


const dialog = useDialog();

const handleContextMenuSelect = (key: string) => {
    switch (key) {
        case 'editAffiliate':
            showEditDrawer.value = true;
            showContextMenu.value = false;
            break;
        case 'disableAffiliate':
            // disableAffiliate(selectedRow.value!.id);
            dialog.warning({
                title: 'Disable Affiliate',
                content: 'Are you sure you want to disable this affiliate?',
                positiveText: 'Yes',
                negativeText: 'No',
                onPositiveClick: () => disableAffiliate(selectedRow.value!.id),
            });
            break
        case 'enableAffiliate':
            // enableAffiliate(selectedRow.value!.id);
            dialog.info({
                title: 'Enable Affiliate',
                content: 'Are you sure you want to enable this affiliate?',
                positiveText: 'Yes',
                negativeText: 'No',
                onPositiveClick: () => enableAffiliate(selectedRow.value!.id),
            });
            break
        default:

            break;
    }
};


const affiliates = ref<Affiliate[]>([]);
const schema = ref([]);
const showAddDrawer = ref(false);
const showEditDrawer = ref(false);

onMounted(() => {
    getAffiliates();
    loading.value = false;
});


const getAffiliates = async () => {
    loading.value = true;
    const { data } = await list();
    affiliates.value = data.data;
    schema.value = data.columns;
    loading.value = false;
};


const page = ref(1);



import { useMessage } from 'naive-ui';

const showSpin = computed(() => loading.value);


const message = useMessage();
const loading = ref(true);
const onCreate = async (formData: any) => {
    try {
        loading.value = true;
        showAddDrawer.value = false;
        await new Promise((resolve) => setTimeout(resolve, 1000)); // Delay of 1000ms
        const { data } = await create(formData);
        affiliates.value = [...affiliates.value, data];
        message.success('Affiliate created successfully');
    }
    catch (err: any) {
        message.error(err.message);
        showAddDrawer.value = true;
    }
    finally {

        loading.value = false;
    }
};

// use update function to update affiliate
const onUpdate = async (formData: any) => {
    const id = selectedRow.value!.id;
    try {
        loading.value = true;
        showEditDrawer.value = false;
        await new Promise((resolve) => setTimeout(resolve, 200)); // Delay of 1000ms
        const { data } = await update(id, formData);
        affiliates.value = affiliates.value.map((affiliate) => {
            if (affiliate.id === data.id) {
                return data;
            }
            return affiliate;
        });
        message.success('Affiliate updated successfully');
    }
    catch (err: any) {
        message.error(err.message);
        showEditDrawer.value = true;
    }
    finally {

        loading.value = false;
    }
};

// create onSubmit function that create affiliate and returns promise



const disableAffiliate = async (id: number | string) => {
    try {
        const { data } = await disable(id);

        const _aff = data.data;
        affiliates.value = affiliates.value.map((affiliate) => {
            if (affiliate.id === id) {
                return _aff;
            }
            return affiliate;
        });
        message.success('Affiliate disabled successfully');
    }
    catch (err: any) {
        message.error(err.message);
    }
    finally {
        // close context menu
        showContextMenu.value = false;
    }
};


const enableAffiliate = async (id: number | string) => {
    try {
        const { data } = await enable(id);

        const _aff = data.data;
        affiliates.value = affiliates.value.map((affiliate) => {
            if (affiliate.id === id) {
                return _aff;
            }
            return affiliate;
        });
        message.success('Affiliate enabled successfully');
    }
    catch (err: any) {
        message.error(err.message);
    }
    finally {
        // close context menu
        showContextMenu.value = false;
    }
};

</script>
  
<style lang="scss">
.list-view {
    a {
        color: var(--primary-color) !important;
        text-decoration: none;
    }

    .plus-icon.n-button {

        transition: all 0.3s ease-in-out;

        &:hover {
            transform: rotate(90deg);
        }

        &:hover {
            color: inherit;
        }
    }
}
</style>
  