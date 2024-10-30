<template>
	<n-card class="settings">
		<n-form ref="refForm" :label-width="80" :model="formValue" :rules="formRules">
			<div class="title">General</div>
			<div class="flex flex-col gap-4 md:flex-row">
				<n-form-item label="First Name" path="first_name" class="flex-grow">
					<n-input v-model:value="formValue.first_name" placeholder="Type first name" />
				</n-form-item>
				<n-form-item label="Last Name" path="last_name" class="flex-grow">
					<n-input v-model:value="formValue.last_name" placeholder="Type last name" />
				</n-form-item>
			</div>

			<div class="flex flex-col gap-4 md:flex-row">
				<n-form-item label="Company Name" path="company_name" class="flex-grow">
					<n-input v-model:value="formValue.company_name" placeholder="Type company name" />
				</n-form-item>
				<n-form-item label="Email" path="email" class="flex-grow">
					<n-input v-model:value="formValue.email" placeholder="Type email" />
				</n-form-item>
			</div>


			<n-form-item label="Country" path="country">
				<n-select v-model:value="formValue.country" :options="countryOptions" placeholder="Select country" />
			</n-form-item>

			<div class="flex flex-col gap-4 md:flex-row">
				<n-form-item label="Telegram" path="telegram" class="flex-grow">
					<n-input v-model:value="formValue.telegram" placeholder="Type Telegram username" />
				</n-form-item>
				<n-form-item label="Skype" path="skype" class="flex-grow">
					<n-input v-model:value="formValue.skype" placeholder="Type Skype username" />
				</n-form-item>
			</div>
			<!-- <div class="title">Settings</div>
			<div class="flex flex-col gap-4 md:flex-row">
				<n-form-item label="Password" path="password" class="flex-grow">
					<n-input v-model:value="formValue.password" type="password" placeholder="Type password" />
				</n-form-item>
				<n-form-item label="Confirm Password" path="password_confirmation" class="flex-grow">
					<n-input v-model:value="formValue.password_confirmation" type="password"
						placeholder="Confirm password" />
				</n-form-item>
			</div> -->

			<n-form-item>
				<n-button @click="onSave" :loading="loading" type="primary">Save</n-button>
			</n-form-item>
		</n-form>
	</n-card>
</template>
  

<script setup lang="ts">
import { ref } from "vue"
import { NCard, NForm, NFormItem, NInput, NButton, NSelect } from "naive-ui"

const formValue = ref({
	company_name: "A Company",
	email: "omri@efra.im",
	first_name: "Omri",
	last_name: "Efraim",
	country: "US",
	telegram: "@omri",
	skype: "omri",
	password: "111111",
	password_confirmation: "111111"
})
const refForm = ref()


const loading = ref(false)


const formRules = {
	username: {
		required: true,
		message: "Please input username",
		trigger: "blur"
	},
	email: {
		required: true,
		message: "Please input email",
		trigger: "blur"
	}
}
const countryOptions = [
	{ label: 'United States', value: 'US' },
	{ label: 'Canada', value: 'CA' },
	{ label: 'Mexico', value: 'MX' },
];


const onSave = () => {
	loading.value = true
	refForm.value.validate((valid) => {
		if (valid) {
			setTimeout(() => {
				loading.value = false
			}, 1000)
		} else {
			loading.value = false
		}
	})
}


</script>

<style lang="scss" scoped>
.settings {
	.title {
		font-size: 20px;
		margin-bottom: 20px;

		&:not(:first-child) {
			margin-top: 20px;
		}
	}
}
</style>
