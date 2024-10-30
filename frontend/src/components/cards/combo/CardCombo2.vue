<template>
	<n-card>
		<div class="flex items-center h-full">

			<div class="card-wrap flex  gap-4"
				:class="{ 'items-center': centered, 'text-center': centered, 'flex-col': !horizontal }">
				<div class="icon" v-if="!loading">
					<slot name="icon"></slot>
				</div>
				<n-skeleton animated v-else width="35px" height="35px" circle />
				<div class="info flex flex-col">
					<!-- Conditional rendering based on loading state -->
					<n-skeleton v-if="loading" animated width="70px" height="25px" />
					<template v-else>
						<div class="value">{{ valueString }}</div>
						<div class="title">{{ title }}</div>
					</template>
					<n-skeleton v-if="loading" animated class="mt-4" height="20px" />
				</div>
			</div>
		</div>
	</n-card>
</template>
  
<script setup lang="ts">
import { faker } from "@faker-js/faker"
import { NCard, NSkeleton } from "naive-ui"
import { toRefs, computed, ref } from "vue"
import { MetricType } from "@/types/analytics"



const props = defineProps<{
	title: string
	val?: number
	currency?: string
	centered?: boolean
	horizontal?: boolean
	value: number
	loading?: boolean
	type?: MetricType
}>()
const { title, val, currency, centered, horizontal, value, loading, type } = toRefs(props)

const valueString = computed(() => {
	if (type?.value === MetricType.Currency) {
		return new Intl.NumberFormat("en-EN", { style: "currency", currency: "USD", minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(value?.value)
	}
	else if (type?.value === MetricType.Percentage) {
		return new Intl.NumberFormat("en-EN", { style: "percent" }).format(value?.value)
	}
	else {
		return new Intl.NumberFormat("en-EN").format(value?.value)
	}
})
</script>

<style scoped lang="scss">
.n-card {
	.card-wrap {
		width: 100%;
		min-width: 100px;

		.title {
			font-size: 18px;
			word-break: initial;
		}

		.value {
			font-family: var(--font-family-display);
			font-size: 22px;
			font-weight: bold;
			margin-bottom: 6px;
		}
	}
}
</style>
