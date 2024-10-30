<template>
    <n-input-group>
        <n-popselect trigger="click" :options="dateOptions" @update:value="handlePopSelect" v-model:value="selectedOption">
            <n-button :render-icon="renderIcon('carbon:time')" type="">
                {{ selectedLabel }}
            </n-button>
        </n-popselect>
        <n-date-picker :on-update:formatted-value="Test()" ref="datePickerRef" v-model:value="customDateRange"
            :max-width="10" type="daterange" clearable end-placeholder="End date" start-placeholder="Start date"
            @update:value="handleDateRangeSelect" />
    </n-input-group>
</template>
  
<script>
import { ref, computed } from 'vue';
import { NButton, NDatePicker, NInputGroup, NPopselect } from 'naive-ui';
import { renderIcon } from "@/utils"

export default {
    name: 'TimeRange',
    components: {
        NButton,
        NDatePicker,
        NInputGroup,
        NPopselect
    },
    emits: ['update:range'], // Declare the event to emit
    setup(props, { emit }) {
        const dateOptions = [
            {
                key: 'today',
                label: 'Today',
                value: 'today'
            },
            {
                key: 'yesterday',
                label: 'Yesterday',
                value: 'yesterday'
            },
            {
                key: 'thisWeek',
                label: 'This Week',
                value: 'thisWeek'
            },
            {
                key: 'lastWeek',
                label: 'Last Week',
                value: 'lastWeek'
            },
            {
                key: 'thisMonth',
                label: 'This Month',
                value: 'thisMonth'
            },
            {
                key: 'lastMonth',
                label: 'Last Month',
                value: 'lastMonth'
            },
            {
                key: 'thisYear',
                label: 'This Year',
                value: 'thisYear'
            },
            {
                key: 'lastYear',
                label: 'Last Year',
                value: 'lastYear'
            },
            {
                key: 'custom',
                label: 'Custom',
                value: 'custom'
            }
        ];

        const Test = (a1, a2) => {
            console.log(a1, a2)
        }

        const selectedOption = ref('thisMonth'); // Default selection

        const today = new Date();
        const _thisMonth = {
            'startDate': new Date(today.getFullYear(), today.getMonth(), 1),
            'endDate': new Date(today.getFullYear(), today.getMonth() + 1, 0)
        }

        const customDateRange = ref([_thisMonth.startDate, today]);

        const datePickerRef = ref(null);

        const selectedLabel = computed(() => {
            if (selectedOption.value === 'custom') {
                return 'Custom';
            }
            return dateOptions.find(option => option.key === selectedOption.value)?.label || 'Select Date';
        });

        const openDatePicker = () => {
            if (datePickerRef.value) {
                datePickerRef.value.$el.querySelector('input').click();
            }
        };

        const handlePopSelect = (key) => {
            selectedOption.value = key;
            const today = new Date();
            let startDate, endDate;

            switch (key) {
                case 'today':
                    startDate = new Date(today);
                    endDate = new Date(today);
                    // set date range to today

                    break;
                case 'yesterday':
                    startDate = new Date(today.setDate(today.getDate() - 1));
                    endDate = new Date(startDate);
                    break;
                case 'thisWeek':
                    startDate = new Date(today.setDate(today.getDate() - today.getDay()));
                    endDate = new Date(today.setDate(startDate.getDate() + 6));
                    break;
                case 'lastWeek':
                    startDate = new Date(today.setDate(today.getDate() - today.getDay() - 7));
                    endDate = new Date(today.setDate(startDate.getDate() + 6));
                    break;
                case 'thisMonth':
                    startDate = new Date(today.getFullYear(), today.getMonth(), 1);
                    endDate = new Date(today.getFullYear(), today.getMonth() + 1, 0);
                    break;
                case 'lastMonth':
                    startDate = new Date(today.getFullYear(), today.getMonth() - 1, 1);
                    endDate = new Date(today.getFullYear(), today.getMonth(), 0);
                    break;
                case 'thisYear':
                    startDate = new Date(today.getFullYear(), 0, 1);
                    endDate = new Date(today.getFullYear(), 11, 31);
                    break;
                case 'lastYear':
                    startDate = new Date(today.getFullYear() - 1, 0, 1);
                    endDate = new Date(today.getFullYear() - 1, 11, 31);
                    break;
                case 'custom':
                    // open date picker

                    openDatePicker();
                    return;
            }

            // Update customDateRange for predefined options

            // end date should be the end of the day
            endDate.setHours(23, 59, 59, 999);

            customDateRange.value = [startDate, endDate];
            emit('update:range', [startDate, endDate]);

        };


        const handleDateRangeSelect = (range) => {
            if (range && range.length > 0) {
                selectedOption.value = 'custom';

                const startDate = new Date(range[0]);
                // const endDate = new Date(range[1]);
                // end date should be the end of the day
                const endDate = new Date(range[1]);
                endDate.setHours(23, 59, 59, 999);
                emit('update:range', [startDate, endDate]);
            }
        };

        return {
            dateOptions,
            selectedOption,
            customDateRange,
            selectedLabel,
            handlePopSelect,
            handleDateRangeSelect,
            renderIcon,
            datePickerRef,
            Test
        }

    }
};
</script>
  