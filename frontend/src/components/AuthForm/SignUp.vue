<template>
	<n-form ref="formRef" :model="model" :rules="rules">
		<n-form-item path="email" label="Email">
			<n-input v-model:value="model.email" @keydown.enter="signUp" size="large" placeholder="Example@email.com" />
		</n-form-item>
		<n-form-item path="firstName" label="First Name">
			<n-input v-model:value="model.firstName" @keydown.enter="signUp" size="large" placeholder="John" />
		</n-form-item>
		<n-form-item path="lastName" label="Last Name">
			<n-input v-model:value="model.lastName" @keydown.enter="signUp" size="large" placeholder="Doe" />
		</n-form-item>
		<n-form-item path="password" label="Password">
			<n-input v-model:value="model.password" type="password" @keydown.enter="signUp" size="large"
				show-password-on="click" placeholder="At least 8 characters" />
		</n-form-item>
		<n-form-item path="confirmPassword" label="Confirm Password" first>
			<n-input v-model:value="model.confirmPassword" type="password" :disabled="!model.password"
				@keydown.enter="signUp" size="large" show-password-on="click" placeholder="At least 8 characters" />
		</n-form-item>
		<div class="flex flex-col items-end">
			<div class="w-full">
				<n-button type="primary" @click="signUp" class="!w-full" size="large">Create an account</n-button>
			</div>
		</div>
	</n-form>
</template>

<script lang="ts" setup>
import { ref } from "vue"

import {
	type FormInst,
	type FormValidationError,
	useMessage,
	type FormRules,
	NForm,
	NFormItem,
	NInput,
	NButton,
	type FormItemRule
} from "naive-ui"
import { useAuthStore } from "@/stores/auth"
import { useRouter } from "vue-router"
import { tr } from "@faker-js/faker";

interface ModelType {
	email: string | null
	firstName: string | null
	lastName: string | null
	password: string | null
	confirmPassword: string | null
}

const router = useRouter()
const formRef = ref<FormInst | null>(null)
const message = useMessage()
const model = ref<ModelType>({
	email: "test@test.com",
	firstName: "John",
	lastName: "Doe",
	password: "password",
	confirmPassword: "password"
})

const rules: FormRules = {
	email: [
		{
			required: true,
			trigger: ["blur"],
			message: "Email is required"
		}
	],
	firstName: [
		{
			required: true,
			trigger: ["blur"],
			message: "First Name is required"
		}
	],
	lastName: [
		{
			required: true,
			trigger: ["blur"],
			message: "Last Name is required"
		}
	],
	password: [
		{
			required: true,
			trigger: ["blur"],
			message: "Password is required"
		}
	],
	confirmPassword: [
		{
			required: true,
			trigger: ["blur"],
			message: "confirmPassword is required"
		},
		{
			validator: (rule: FormItemRule, value: string): boolean => {
				return value === model.value.password
			},
			message: "Password is not same as re-entered password!",
			trigger: ["blur", "password-input"]
		}
	]
}

function signUp(e: Event) {
	e.preventDefault()
	formRef.value?.validate(async (errors: Array<FormValidationError> | undefined) => {
		if (!errors) {
			try {
				await useAuthStore().register({
					email: model.value.email,
					firstName: model.value.firstName,
					lastName: model.value.lastName,
					password: model.value.password
				})

				message.success("Sign up successful")
				
				await useAuthStore().fetchToken({
					email: model.value.email,
					password: model.value.password
				}, false);
				// check if there's redirect query
				const redirect = router.currentRoute.value.query.redirect;
				message.success("Successfully logged in");
				if (redirect) {
					router.push({ path: redirect as string, replace: true });
				} else {
					router.push({ path: "/", replace: true });
				}
				
			} catch (error: any) {
				if (error.response.data.error == "Email already exists") {
					message.error("User already exists")
				} 
			}
			// if (model.value.email === "admin@admin.com" && model.value.password === "password") {
			// 	useAuthStore().setLogged()
			// 	router.push({ path: "/", replace: true })
			// } else {
			// 	message.error("Invalid credentials")
			// }
		} else {
			message.error("Invalid credentials")
		}
	})
}
</script>
