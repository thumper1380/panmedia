<!-- Dashboard.vue -->
<template>
    <div class="page">
        <div class="metrics-group mb-5">
            <n-input-group class="mb-5">
                <TimeRange @update:range="handleDateRangeUpdate" />

                <!-- Refresh button -->
                <n-button v-if="!isMobile()" size="medium" :text="true" :bordered="false" :focusable="false"
                    @click="handleDateRangeUpdate([new Date('2024-02-19'), new Date('2024-06-19')])">
                    <Icon name="ion:refresh" :size="20" />
                </n-button>
            </n-input-group>

            <Metrics :loading="loading" :metrics="metrics" />
        </div>
        <div class="main-grid gap-5">
            <!-- Metrics and Group Input -->

            <div class="chart">
                <CardCombo3 :loading="loading" :chartData="chartData" class="flex h-full"
                    @update:loaded="loading = $event" />
            </div>

            <!-- Top Countries component -->
            <div class="top-countries">
                <top-advertisers :loading="loading" class="flex h-full" />
            </div>

            <!-- Top Advertisers component -->
            <div class="top-advertisers">
                <top-countries :loading="loading" class="flex h-full" />

            </div>

            <!-- Top Affiliates component -->
            <div class="latest-conversions">
                <latest-conversions :loading="loading" class="flex h-full" />
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">

import { useThemeStore } from "@/stores/theme"
import { computed, defineComponent, h, ref, toRefs, onMounted, onBeforeMount } from "vue"
import { NCarousel, NCard, NButton, NDataTable, NDropdown, NFlex, NInputGroup, NDatePicker, NScrollbar, NRow, NCol, NGi, NGrid } from "naive-ui"
import Icon from "@/components/common/Icon.vue"
import TimeRange from "@/components/TimeRange.vue"
import { metrics as fetchMetrics, registrationChart as fetchRegistrationChart } from "@/services/analyticsService"
import CardCombo1 from "@/components/cards/combo/CardCombo1.vue"
import Metrics from "@/components/dashboard/Metrics.vue"
import CardCombo3 from "@/components/cards/combo/CardCombo3.vue"
// import isMobile
import { isMobile } from "@/utils"
import TopCountries from "@/components/dashboard/TopCountries.vue"
import TopAdvertisers from "@/components/dashboard/TopAdvertisers.vue"
import LatestConversions from "@/components/dashboard/LatestConversions.vue"

const CompletedIcon = "carbon:checkmark-filled"

const SalesIcon = "carbon:shopping-cart"
const CursorIcon = "fluent:cursor-24-regular"
const RegisterIcon = "fluent:people-team-20-regular"
const RevenueIcon = "carbon:currency-dollar"

// circle-flags:br

const brazilFlag = "circle-flags:br"

const UsersIcon = "carbon:users"

const showExpandButton = ref(true)
const ExpandIcon = "fluent:expand-up-right-24-regular"
const ContractIcon = "fluent:contract-down-left-24-regular"
const ReloadIcon = "tabler:refresh"
const MenuIcon = "carbon:overflow-menu-vertical"
import { renderIcon } from "@/utils"

const props = defineProps<{
    showActions?: boolean
    showDate?: boolean
    minWidth?: number
    tableRows?: number
    reload?: (state: boolean) => void
    expand?: (state: boolean) => void
    isExpand?: () => boolean,
}>()

// define name of component
defineOptions({
    name: "Toolbar"
})

const timeRangeValue = ref(["2021-01-01", "2021-12-31"])


const { showActions, showDate, minWidth, reload, expand, isExpand } = toRefs(props)

const menuOptions = computed(() =>
    showExpandButton.value
        ? [
            {
                label: "Expand",
                key: "expand",
                icon: renderIcon(ExpandIcon)
            },
            {
                label: "Reload",
                key: "reload",
                icon: renderIcon(ReloadIcon)
            }
        ]
        : [
            {
                label: "Collapse",
                key: "collapse",
                icon: renderIcon(ContractIcon)
            },
            {
                label: "Reload",
                key: "reload",
                icon: renderIcon(ReloadIcon)
            }
        ]
)
let reloadTimeout: NodeJS.Timeout | null = null

function menuSelect(key: string) {
    if (key === "expand") {
        expand?.value && expand?.value(true)
    }
    if (key === "collapse") {
        expand?.value && expand?.value(false)
    }
    if (key === "reload") {
        reload?.value && reload?.value(true)

        if (reloadTimeout) {
            clearTimeout(reloadTimeout)
        }

        reloadTimeout = setTimeout(() => {
            reload?.value && reload?.value(false)
        }, 1000)
    }
}




const style = computed<{ [key: string]: any }>(() => useThemeStore().style)
const textSecondaryColor = computed<string>(() => style.value["--fg-secondary-color"])

const chartBg = computed<string>(() =>
    useThemeStore().isThemeDark ? style.value["--secondary1-color"] : style.value["--secondary1-color"]
)


// fetch metrics
const metrics = ref<any>([])


onMounted(() => {
    if (isExpand?.value) {
        showExpandButton.value = !isExpand?.value()
    }
})

const metric = ref<any>(null)

const startDate = ref(new Date().toISOString().split('T')[0])
const endDate = ref(new Date().toISOString().split('T')[0])


const chartData = ref<any>([])
onBeforeMount(async () => {
    const metricResponse = await fetchMetrics(startDate.value, endDate.value)
    metrics.value = metricResponse.data

    const registrationChartResponse = await fetchRegistrationChart(startDate.value, endDate.value)
    chartData.value = registrationChartResponse.data
    console.log('chartData', chartData.value)

})



const loading = ref(false)

const handleDateRangeUpdate = async (dateRange: [Date, Date]) => {
    loading.value = true
    console.log('Selected Date Range:', dateRange);
    const [start, end] = dateRange;
    startDate.value = start.toISOString().split('T')[0]
    endDate.value = end.toISOString().split('T')[0]
    const metricResponse = await fetchMetrics(startDate.value, endDate.value)
    metrics.value = metricResponse.data

    const registrationChartResponse = await fetchRegistrationChart(startDate.value, endDate.value)
    chartData.value = registrationChartResponse.data

    console.log('chartData', chartData.value)


    setTimeout(() => {
        loading.value = false
    }, 500)


    // Do something with dateRange, e.g., update data properties, make API calls, etc.
}

const columns = [
    {
        title: '#',
        key: 'position',

    },
    {
        title: 'Advertiser',
        key: 'advertiser',

    },
    {
        title: 'Sales',
        key: 'sales',
        width: 70
    },
    {
        title: 'Revenue',
        key: 'revenue',
        width: 100
    },
    {
        title: 'Payout',
        key: 'payout',
        width: 100
    },
    {
        title: 'Profit',
        key: 'profit',
        width: 100
    },
    {
        title: 'CR',
        key: 'cr',
        width: 70
    }
]
const data = [
    {
        position: '1',
        advertiser: 'Alice Johnson',
        sales: '150',
        revenue: '$1500',
        payout: '$700',
        profit: '$800',
        cr: '60%'
    },
    {
        position: '2',
        advertiser: 'Michael Smith',
        sales: '120',
        revenue: '$1100',
        payout: '$600',
        profit: '$500',
        cr: '55%'
    },
    {
        position: '3',
        advertiser: 'Sara Davis',
        sales: '90',
        revenue: '$950',
        payout: '$450',
        profit: '$500',
        cr: '45%'
    },
    {
        position: '4',
        advertiser: 'James Wilson',
        sales: '80',
        revenue: '$800',
        payout: '$400',
        profit: '$400',
        cr: '40%'
    },
    {
        position: '5',
        advertiser: 'Emma Brown',
        sales: '200',
        revenue: '$2000',
        payout: '$1000',
        profit: '$1000',
        cr: '70%'
    },
    // ... Add more entries as needed
];


</script>
<style lang="scss" scoped>
@import "@/assets/scss/common.scss";


.page {
    .main-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        grid-template-rows: auto;
        /* Adjust the gap size as needed */

        grid-template-areas:
            "chart table"
            "advertisers affiliates";

        @media (max-width: 768px) {
            grid-template-columns: repeat(1, minmax(0, 1fr));
            grid-template-areas:
                "chart"
                "table"
                "advertisers"
                "affiliates";
            ;
        }
    }

    .metrics-group {
        grid-area: metrics;
    }

    .chart {
        grid-area: chart;
    }

    .top-countries {
        grid-area: table;
    }

    .top-advertisers {
        grid-area: advertisers;
    }

    .top-affiliates {
        grid-area: affiliates;
    }

}
</style>
