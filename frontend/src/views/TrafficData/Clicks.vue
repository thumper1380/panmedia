<template>
    <div class="page click-list">
        <n-spin :show="showSpin" class="h-full">
            <n-card class="flex h-full" :size="isMobile() ? 'medium' : 'medium'">

                <template #header-extra>
                    <!-- <n-switch v-model:value="countryColumnVisible" style="margin-right: 10px" /> -->
                    <n-space>
                        <n-button :native-focus-behavior="true" text :disabled="tableLoading" size="small"
                            :focusable="false" @click="reloadTable"
                            :class="{ 'rotating': tableLoading, 'tool-bar-button': true }">
                            <Icon name="carbon:renew" :size="18" />
                        </n-button>
                        <n-button :native-focus-behavior="true" text v-if="isMobile()" :disabled="tableLoading" size="small"
                            :focusable="false" @click="showFiltersDrawer = true">
                            <Icon name="ion:filter" :size="20" />
                        </n-button>
                        <n-button :native-focus-behavior="true" text v-if="isMobile()" :disabled="tableLoading" size="small"
                            :focusable="false" @click="showTableSettingsDrawer = true">
                            <Icon name="carbon:settings" :size="20" />
                        </n-button>
                        <n-dropdown v-if="!isMobile()" :options="dropDownOptions" @select="handleDropDownselect"
                            trigger="click" placement="bottom-end">
                            <n-button on text size="small">
                                <Icon name="carbon:overflow-menu-vertical" :size="20" />
                            </n-button>
                        </n-dropdown>
                    </n-space>
                    <!-- switch for country column -->
                </template>
                <template #header>
                    <span v-if="isMobile()">
                        Clicks
                    </span>
                    <dynamic-tag-select v-show="!isMobile()" :values="filters.state"
                        @update:values="handleStateUpdate" :options="dynamicTagSelectOptions" />
                </template>

                <n-space justify="center" align="center">
                    <div>
                        <n-data-table remote table-layout="auto" :row-props="rowProps" :max-height="tableHeight"
                            :data="data" striped :row-key="row => row.id" :columns="tableColumns" :bordered="!isMobile()">

                        </n-data-table>

                        <n-flex :justify="isMobile() ? 'center' : 'flex-end'" :class="isMobile() ? 'mt-5' : 'mt-5'">
                            <n-pagination v-model:page="pagination.page" :page-sizes="[20, 30, 40, 50]"
                                :on-update:page-size="updatePageSize" :page-count="pageCount" @update-page="fetchData(200)"
                                :show-size-picker="!isMobile()" size="medium" />
                        </n-flex>
                    </div>
                    <n-empty v-if="false" style="height: 200px">
                        <template #default>
                            <!-- a description message -->
                            Please select a preset or generate a report to view data.
                        </template>
                        <template #icon>
                            <n-icon>
                                <Icon name="carbon:analytics" :size="30" />
                            </n-icon>
                        </template>
                        <template #extra>
                            <n-button secondary type="primary" @click="createPreset">
                                Create Preset
                            </n-button>
                        </template>
                    </n-empty>
                </n-space>






                <n-dropdown :animated="true" :on-select="handleContextMenuSelect"
                    :on-clickoutside="() => showContextMenu = false" placement="bottom-start" trigger="manual" :x="x" :y="y"
                    :options="contextMenuOptions" :show="showContextMenu">
                </n-dropdown>
            </n-card>
        </n-spin>
        <settings :columnsConfig="columnsConfig" :filters="filters" :show="showTableSettingsDrawer" @update:show="showTableSettingsDrawer = $event"
            @update:columnsConfig="updateColumnsConfig" />

        <filters :columns="tableColumns" :columnsConfig="columnsConfig" @update:filters="handleFilterUpdate"
           :show="showFiltersDrawer" @update:show="showFiltersDrawer = $event" />

    </div>
</template>
  
<script setup lang="ts">
import { toRefs, ref, h, nextTick, onBeforeMount, onMounted, computed } from 'vue';
import { NIcon,NEmpty, NSpin, NCard, NDataTable, NButton, NSpace, NDivider, NIconWrapper, NDropdown, NPagination, NFlex, NSwitch, NEllipsis, useDialog, NSkeleton } from 'naive-ui';
import Icon from '@/components/common/Icon.vue';
import { RouterLink } from 'vue-router';
import { renderIcon } from '@/utils';
import type { DropdownOption, DataTableColumns } from 'naive-ui'
import Settings from '@/components/TrafficData/Settings.vue';
import Filters from '@/components/TrafficData/Filters.vue';
import DynamicTagSelect from '@/components/DynamicTagSelect.vue';
import type { TrafficData } from '@/types/trafficdata';
import { list, columns as getColumns } from '@/services/trafficdataService';
import { saleStatuses } from '@/services/settingsService';
import type { SaleStatus } from '@/types/settings';
import { isMobile } from '@/utils';
import renderColumn from '@/utils/table';
import ColorTag from '@/components/ColorTag.vue';


const props = defineProps({
    // detailView route name
    detailView: {
        type: String,
        default: 'ClicksDetails'
    },
    // initialStates
    initialStates: {
        type: Array,
        default: () => ['click', 'click_landed', 'lead', 'lead_pushed']
    }
});

// compute dummy empty rows according to page size and columns
// const dummyEmptyTableData 
// array with 12 empty dicts
const dummyEmptyTableData = computed(() => {
    // return Array.from({ length: 15 }, () => ({}));
    // length as tehe same current data length
    return Array.from({ length: tableData.value.length }, () => ({}));
})

// toRefs
const { detailView, initialStates } = toRefs(props);



const dialog = useDialog();

const dynamicTagSelectOptions = [
    {
        label: 'Click',
        value: 'click',
    },
    {
        label: 'Click Landed',
        value: 'click_landed',
    },
    {
        // lead
        label: 'Lead',
        value: 'lead',
    },
    // lead pushed
    {
        label: 'Lead Pushed',
        value: 'lead_pushed',
    },
    // lead rejected
    {
        label: 'Lead Rejected',
        value: 'lead_rejected',
    },
    // sale
    {
        label: 'Sale',
        value: 'sale',
    },
]


const showTableSettingsDrawer = ref(false);
const showFiltersDrawer = ref(false);

const showSpin = computed(() => {
    return tableLoading.value;
})

const tags = ref([]);
const dropDownOptions = [
    // {
    //     label: 'Reload',
    //     key: 'reload',
    //     icon: renderIcon('carbon:renew'),
    // },
    // settings
    {
        label: 'Filters',
        key: 'filters',
        icon: renderIcon('ion:options-outline'),
    },
    {
        label: 'Settings',
        key: 'settings',
        icon: renderIcon('carbon:settings'),
    },
];

const handleDropDownselect = (key: string | number, option: DropdownOption) => {
    if (key === 'settings') {
        showTableSettingsDrawer.value = true;
        return
    }
    else if (key === 'filters') {
        showFiltersDrawer.value = true;
        return
    }
    else if (key === 'reload') {
        reloadTable();
        return
    }
}



const tableData = ref([] as TrafficData[]);

const data = computed(() => {
    // if table is loading return dummy data
    if (tableLoading.value) {
        return dummyEmptyTableData.value;
    }
    return tableData.value;
})



const tableLoading = ref(false);

const reloadTable = async () => {
    tableLoading.value = true;
    // clear table data
    // tableData.value = [];
    setTimeout(async () => {
        await fetchData();
        tableLoading.value = false;
    }, 200);
}


const countryColumnVisible = ref(true);


const columnsConfig = ref([]);


const tableHeight = ref('calc(75vh - var(--toolbar-height) - var(--view-padding) - var(--view-padding) / 2)');


const onClickOutSide = (e: MouseEvent) => {
    showContextMenu.value = false;
}

// import useMessage
import { useMessage } from 'naive-ui';
const message = useMessage();

const x = ref(0);
const y = ref(0);
const showContextMenu = ref(false);

const rowProps = (row: TrafficData) => {
    return {
        onContextmenu: (e: MouseEvent) => {
            showContextMenu.value = false
            selectedRow.value = null;

            e.preventDefault()
            nextTick().then(() => {
                showContextMenu.value = true
                x.value = e.clientX
                y.value = e.clientY
                // set selected row
                selectedRow.value = row;
            })
        }
    }
}

import { useRouter } from 'vue-router';

const router = useRouter();


const handleContextMenuSelect = (key: string | number, option: DropdownOption) => {
    // message.info(`${JSON.stringify(option, null, 2)}`);
    showContextMenu.value = false;
    // if view go to view page
    if (key === 'view') {
        router.push({
            name: 'ClicksDetails',
            params: {
                id: selectedRow.value?.id
            }
        })
        return
    }
    else if (key === 'reinject') {
        dialog.warning({
            title: 'Reinject',
            content: 'Are you sure you want to reinject this lead?',
            positiveText: 'Yes',
            negativeText: 'No',
            onPositiveClick: async () => {
                message.info('Reinjecting click');
            }
        })
    }
    // show selected row
    else if (selectedRow.value) {
        message.info(`${key} ${selectedRow.value.id}`);
    }

}

const selectedRow = ref<TrafficData | null>(null);

const contextMenuOptions: DropdownOption[] = [
    {
        label: 'View',
        key: 'view',
        icon: renderIcon('carbon:view'),
    },
    {
        label: 'Reinject',
        key: 'reinject',
        icon: renderIcon('carbon:insert'),
    },
    {
        label: 'Duplicate',
        key: 'duplicate',
        icon: renderIcon('carbon:user-multiple'),
    },
    {
        label: 'Status',
        key: 'status',
        icon: renderIcon('ion:receipt-outline'),
        children: [
            {
                label: 'New',
                key: 'new',
            },
            {
                label: 'Pending Payment',
                key: 'pending_payment',
            },
            {
                label: 'Completed',
                key: 'completed',
            },
            {
                label: 'Cancelled',
                key: 'cancelled',
            },
            {
                type: 'divider',
            },
            {
                // render with top divider
                label: 'Manual',
                key: 'manual',
                // type: 'divider',
            }
        ]
    }
]





const filters = ref({
    state: ref(initialStates.value),
})

const pagination = ref({
    page: 1,
    pageSize: 15,
    totalItems: 0,
});
// compute page count 
const pageCount = computed(() => {
    return Math.ceil(pagination.value.totalItems / pagination.value.pageSize);
});

// compute filters for use in params should be generic

interface Filters {
    [key: string]: string[];
    // Add more specific properties if needed
}

interface TransformedFilters {
    [key: string]: string;
}


const transformFilters = (filters: Filters): TransformedFilters => {
    const transformed: TransformedFilters = {};
    for (const key in filters) {
        // Assuming each filter is an array of strings
        if (Array.isArray(filters[key])) {
            transformed[key] = filters[key].join(',');
        }
    }
    return transformed;
};




const fetchData = async (delay = 0) => {
    // clear table data
    // tableData.value = [];
    tableLoading.value = true;
    try {

        const params = {
            page: pagination.value.page,
            page_size: pagination.value.pageSize,
            ordering: '-created_at',
            ...transformFilters(filters.value)
        };
        const res = await list(params); // Adjust this to pass params to your API call

        await new Promise(resolve => setTimeout(resolve, delay)); // Add delay here

        tableData.value = res.data.results; // Adjust according to your API response structure
        pagination.value.totalItems = res.data.count;
    } catch (error: any) {
        // check if 404 
        if (error.response.status === 404) {
            // show message
            message.error('No data found');
        }
        else {
            // show message
            message.error('Something went wrong');
        }
        tableData.value = [];
    } finally {
        tableLoading.value = false;
    }
};



const updatePageSize = (pageSize: number) => {
    pagination.value.pageSize = pageSize;
    pagination.value.page = 1;
    fetchData();
};

const handleFilterUpdate = (newFilters: any) => {
    // Update your filter state and fetch data
    resetPagination();
    showFiltersDrawer.value = false;
    filters.value = newFilters;
    fetchData();
};

const handleStateUpdate = (newFilters: any) => {
    // Update your filter state and fetch data
    resetPagination();
    filters.value.state = newFilters;
    fetchData();
};

const resetPagination = () => {
    pagination.value.page = 1;
    pagination.value.pageSize = 20;
    pagination.value.totalItems = 0;
}


const fetchColumns = async () => {
    try {
        const { data } = await getColumns();
        // Enhance each column config with a visibility property
        // columnsConfig.value = data.map((column: any[]) => ({
        //     ...column,
        //     visible: true // Set initial visibility; can be dynamic based on user preferences
        // }));
        columnsConfig.value = data;
    } catch (err) {
        // Handle errors
    }
}


const updateColumnsConfig = (newConfig: any) => {
    console.log(newConfig);
    showTableSettingsDrawer.value = false;
    columnsConfig.value = newConfig;
};

const unvisibleColumns: string[] = []

const saleStatusesConf = ref<SaleStatus[]>([]);

const tableColumns = computed(() => {
    // Filter out columns that are not visible
    return columnsConfig.value
        .filter(column => column.visible)
        .map(column => ({
            ...column as any,
            render: (row: any) => renderColumn(detailView.value, row, column)
        }));
});



const fetchSaleStatuses = async () => {
    return new Promise(async (resolve, reject) => {
        try {
            const { data } = await saleStatuses();
            saleStatusesConf.value = data;
            resolve(data);
        }
        catch (err: any) {
            reject(err);
        }
    })
}



onBeforeMount(async () => {
    fetchSaleStatuses();
    fetchColumns();
    // nextTick().then(() => {
    // })
    document.querySelector('.n-card')?.addEventListener('contextmenu', (e) => {
        e.preventDefault();
    })

})


onMounted(async () => {
    fetchData();
})


</script>
  
<style lang="scss">
@import "@/assets/scss/mixin.scss";


.page-wrapped {
    // height: calc(100svh - var(--toolbar-height) - var(--view-padding) - var(--view-padding) / 2);
}

.page.click-list {
    // @media (max-width: 700px) {
    //     @include page-full-view;
    // }

    /* set a as primary color without underline */
    a {
        color: var(--primary-color) !important;
        text-decoration: none;

    }

    .rotating {
        animation: rotating 2s linear infinite;
    }

    @keyframes rotating {
        from {
            transform: rotate(0deg);
        }

        to {
            transform: rotate(360deg);
        }
    }

    // rotate icon on hover
    .n-icon {
        transition: transform 0.3s ease, color 0.3s ease;

        &:hover {
            transform: rotate(360deg);
        }
    }

    // tool-bar-button hover rotate
    .tool-bar-button {
        transition: transform 0.3s ease;

        &:hover {
            transform: rotate(30deg);
        }
    }

    // .n-card__content{
    //     padding: 0;
    // }
    // on mobile content padding 0
    .n-card__content {
        @media (max-width: 700px) {
            padding-right: 0;
            padding-left: 0;
        }
    }

    // disable button hover color
    .n-button {
        &:hover {
            color: inherit;
        }

        &:focus {
            color: inherit;
        }
    }

}
</style>
  