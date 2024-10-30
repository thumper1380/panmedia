<template>
    <div class="page drill-down">
        <n-card>

            <template #header>
                <n-flex>

                    Drilldown Reports
                    <!-- question mark button icon -->
                    <n-button text type="primary">
                        <Icon :size="16" name="carbon:help" />
                    </n-button>
                </n-flex>
            </template>
            <template #header-extra>
                <!-- create preset button -->
                <n-button type="primary" size="medium" @click="createPreset">
                    <!-- <Icon name="carbon:add" :size="12" /> -->
                    Create Preset
                </n-button>
            </template>
            <template #default>
                <n-form ref="formRef" label-placement="top">
                    <!-- Presets and Date Range Selection -->
                    <n-grid :span="24" :x-gap="12">

                        <n-form-item-gi :span="5" label="Preset">
                            <n-select v-model:value="presetValue" :options="presetOptions" />
                        </n-form-item-gi>
                        <n-form-item-gi :show-feedback="false" :span="19" label="Group By">
                            <DynamicGroupFields v-model:modelValue="dynamicGroupInput" :options="fieldOptions" />
                        </n-form-item-gi>
                        <n-form-item-gi :span="10" label="Date Range">
                            <TimeRange />
                        </n-form-item-gi>
                        <n-form-item-gi :span="3" label="Time Zone">
                            <n-select filterable :options="timezoneOptions" placeholder="Select Time Zone" />
                        </n-form-item-gi>

                        <n-grid-item :span="24">
                            <n-collapse arrow-placement="right" :trigger-areas="['arrow', 'main']">
                                <n-collapse-item name="settings">
                                    <template #header>
                                        <!-- <n-button secondary type="primary"> -->
                                        <!-- <Icon :size="16" name="carbon:settings" /> -->
                                        Settings
                                        <!-- </n-button> -->
                                    </template>
                                    <template #arrow>
                                        <!-- <Icon :size="16" name="carbon:add" /> -->
                                        <!-- <span>  </span> -->
                                    </template>
                                    <n-grid :x-gap="12" :span="12">
                                        <n-form-item-gi :span="4" label="Field">
                                            <n-select :options="fieldOptions" />
                                        </n-form-item-gi>
                                        <n-form-item-gi :span="4" label="Sign">
                                            <n-select :options="fieldOptions" />
                                        </n-form-item-gi>
                                        <n-form-item-gi :span="4" label="Value">
                                            <n-select :options="fieldOptions" />
                                        </n-form-item-gi>
                                        <n-form-item-gi :span="2">
                                            <n-button dashed size="medium" type="primary">
                                                +
                                            </n-button>
                                        </n-form-item-gi>
                                    </n-grid>
                                </n-collapse-item>
                            </n-collapse>
                        </n-grid-item>
                    </n-grid>
                </n-form>

            </template>

        </n-card>

        <!-- create preset card -->
        <n-modal v-model:show="showPresetModal" style="width: 450px" class="custom-card" preset="card" title="Create Preset"
            :bordered="true" size="medium" :closable="false" :segmented="segmented">
            <template #default>
                <n-form>
                    <n-form-item :show-label="false" label="Preset Name">
                        <n-input placeholder="Enter Preset Name" />
                    </n-form-item>
                </n-form>
                <n-flex justify="end" align="center">
                    <n-button type="primary">
                        Save
                    </n-button>
                </n-flex>
            </template>
        </n-modal>

        <n-spin :show="showSpin">
            <n-card style="min-height: 300px" class="mt-5">
                <template #header>
                    <n-flex align="center">
                        Drilldown Data
                        <n-button text type="primary">
                            <Icon :size="18" name="carbon:settings" />
                        </n-button>
                    </n-flex>

                </template>
                <template #header-extra>
                    <n-flex align="center">

                        <!-- <n-dropdown :options="dropDownOptions" trigger="click" placement="bottom-end">
                            <n-button :focusable="false" text size="small">
                                <Icon name="carbon:overflow-menu-vertical" :size="20" />
                            </n-button>
                        </n-dropdown> -->
                        <!-- settings icon -->

                        <n-button :disabled="!data.length" secondary type="primary" size="medium" @click="downloadCSV">
                            Download CSV
                        </n-button>
                        <n-button type="primary" size="medium" @click="generateReport">
                            <!-- <Icon name="carbon:add" :size="12" /> -->
                            Generate Report
                        </n-button>
                    </n-flex>


                </template>

                <n-flex justify="center" align="center">
                    <n-data-table ref="drilldownTableRef" striped v-if="data.length" :max-height="600" :scroll-x="1400"
                        :data="data" :columns="columns" :row-key="row => row.index">

                    </n-data-table>
                    <n-empty style="height: 150px" v-else-if="!showSpin">
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
                </n-flex>
            </n-card>
        </n-spin>
    </div>
</template>
  
<script setup>
import { ref, h } from 'vue';
import {
    NPageHeader,
    NCard,
    NForm,
    NFormItem,
    NFormItemGridItem,
    NSelect,
    NDatePicker,
    NSpace,
    NButton,
    NInput,
    NIcon,
    NBreadcrumb,
    NBreadcrumbItem,
    NStatistic,
    NGrid,
    NGridItem,
    NFlex,
    NFormItemGi,
    NDivider,
    NCollapse,
    NCollapseItem,
    NDataTable,
    NSpin,
    NDropdown,
    NModal,
    NEmpty
} from 'naive-ui';
import Icon from '@/components/common/Icon.vue';
import DynamicGroupFields from '@/components/DynamicGroupFields.vue';

import TimeRange from '@/components/TimeRange.vue';
import { listTimeZones } from 'timezone-support';

const segmented = ref({
    // content: 'soft',

})
const showPresetModal = ref(false);

const showSpin = ref(false);

const formRef = ref();
const presetValue = ref(null);
const presetOptions = ref([
    {
        label: 'Preset 1',
        value: 'preset1'
    },
    {
        label: 'Preset 2',
        value: 'preset2'
    },
    {
        label: 'Preset 3',
        value: 'preset3'
    }
]);
const dateRange = ref({
    start: null,
    end: null
});
const conditions = ref([]);
const fieldOptions = ref([
    {
        label: 'Field 1',
        value: 'field1',
    },
    {
        label: 'Field 2',
        value: 'field2'
    },
    {
        label: 'Field 3',
        value: 'field3'
    }
]);

const dynamicGroupInput = ref([null]);


const signOptions = ref([
    // Define your sign options here
]);
const removeIcon = 'mdi-close-circle';

const addCondition = () => {
    conditions.value.push({
        field: null,
        sign: null,
        value: ''
    });
};



const dropDownOptions = [
    {
        label: 'Download CSV',
        key: 'downloadCSV',
        icon: () => h(Icon, { name: 'carbon:download' })
    },
    // settings
    {
        label: 'Settings',
        key: 'settings',
        icon: () => h(Icon, { name: 'carbon:settings' })
    }
]

const columns = ref([
    { "title": "Name", "key": "name" },
    // { "title": "Index", "key": "index" },
    { "title": "Clicks", "key": "clicks" },
    { "title": "Leads", "key": "leads" },
    { "title": "Sales", "key": "sales" }
]);

const data = ref([])
const _data = ref([
    {
        "name": "Affiliate 1",
        "index": "Affiliate 1",
        "clicks": 33,
        "leads": 15,
        "sales": 6,
        "children": [
            {
                "name": "Country 1",
                "index": "Affiliate 1-Country 1",
                "clicks": 18,
                "leads": 8,
                "sales": 3,
                "children": [
                    {
                        "name": "Advertiser 1",
                        "index": "Affiliate 1-Country 1-Advertiser 1",
                        "clicks": 10,
                        "leads": 5,
                        "sales": 2
                    },
                    {
                        "name": "Advertiser 2",
                        "index": "Affiliate 1-Country 1-Advertiser 2",
                        "clicks": 8,
                        "leads": 3,
                        "sales": 1
                    }
                ]
            },
            {
                "name": "Country 2",
                "index": "Affiliate 1-Country 2",
                "clicks": 15,
                "leads": 7,
                "sales": 3,
                "children": [
                    {
                        "name": "Advertiser 3",
                        "index": "Affiliate 1-Country 2-Advertiser 3",
                        "clicks": 15,
                        "leads": 7,
                        "sales": 3
                    }
                ]
            }
        ]
    },
    {
        "name": "Affiliate 2",
        "index": "Affiliate 2",
        "clicks": 12,
        "leads": 6,
        "sales": 2,
        "children": [
            {
                "name": "Country 3",
                "index": "Affiliate 2-Country 3",
                "clicks": 12,
                "leads": 6,
                "sales": 2,
                "children": [
                    {
                        "name": "Advertiser 4",
                        "index": "Affiliate 2-Country 3-Advertiser 4",
                        "clicks": 12,
                        "leads": 6,
                        "sales": 2
                    }
                ]
            }
        ]
    }
]);




const timezones = listTimeZones();

const timezoneOptions = timezones.map(tz => ({
    label: tz,
    value: tz
}));


const removeCondition = (index) => {
    conditions.value.splice(index, 1);
};

const generateReport = () => {
    // Trigger report generation logic
    showSpin.value = true;
    data.value = [];
    setTimeout(() => {
        showSpin.value = false;
        data.value = _data.value;
    }, 5000);
};


const generateCSVName = () => {
    const date = new Date();
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const timestamp = date.getTime();

    return `report-${year}-${month}-${day}-${timestamp}.csv`;
}

const drilldownTableRef = ref(null);

const downloadCSV = () => {
    // Trigger CSV download logic  
    drilldownTableRef.value?.downloadCsv({
        fileName: generateCSVName(),
    });
};


const createPreset = () => {
    // Trigger preset creation logic
    showPresetModal.value = true;
};

</script>
  

<style lang="scss">
.drill-down {}
</style>
