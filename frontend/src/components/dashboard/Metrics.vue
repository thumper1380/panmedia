<template>
    <n-scrollbar x-scrollable>
        <div class="flex flex-col gap-5" style="white-space: nowrap">
            <!-- 4 cards -->
            <div class="flex gap-5">
                <CardCombo2 :loading="loading" v-for="(metric, index) in metrics" :key="index" centered
                    :value="metric.value" :title="metric.title" :type="metric.type" class="basis-1/6">
                    <template #icon>
                        <CardComboIcon :iconName="metric.icon" boxed :boxSize="35" :color="style['--info-color']">
                        </CardComboIcon>
                    </template>
                </CardCombo2>
            </div>
        </div>
    </n-scrollbar>
</template>


<script setup lang="ts">
import { computed, defineComponent, h, ref, toRefs, onMounted, onBeforeMount } from "vue"
import { NCarousel, NCard, NButton, NDataTable, NDropdown, NSpace, NInputGroup, NDatePicker, NScrollbar, NRow, NCol } from "naive-ui"
import Icon from "@/components/common/Icon.vue"
import TimeRange from "@/components/TimeRange.vue"
import { metrics as fetchMetrics } from "@/services/analyticsService"
import CardCombo1 from "@/components/cards/combo/CardCombo1.vue"
import CardCombo2 from "@/components/cards/combo/CardCombo2.vue"
import { useThemeStore } from "@/stores/theme"
import type { MetricType, MetricData } from "@/types/analytics"





// define props
const props = defineProps({
    metrics: {
        type: Array as () => MetricData[],
        required: true
    },
    loading: {
        type: Boolean,
        default: false
    }
})

const style = computed<{ [key: string]: any }>(() => useThemeStore().style)

const { metrics } = toRefs(props)


</script>