<template>
	<n-form ref="formRef" :model="model" :rules="rules" :disabled="isSigningIn">
		<n-form-item path="email" label="Email">
			<n-input v-model:value="model.email" @keydown.enter="signIn" placeholder="example@email.com" size="large"
				autocomplete="on" />
		</n-form-item>
		<n-form-item path="password" label="Password">
			<n-input v-model:value="model.password" type="password" show-password-on="click"
				placeholder="At least 8 characters" @keydown.enter="signIn" autocomplete="on" size="large" />
		</n-form-item>
		<div class="flex flex-col items-end gap-6">
			<div class="flex justify-between w-full">
				<n-checkbox v-model:checked="rememberMe">Remember me</n-checkbox>
				<n-button text type="primary" @click="emit('forgot-password')">Forgot Password?</n-button>
			</div>
			<div class="w-full">
				<n-button type="primary" @click="signIn" class="!w-full" size="large" :loading="isSigningIn">
					<!-- if loading don't show sign in text -->
					<span v-if="!isSigningIn">Sign in</span>

				</n-button>
			</div>
		</div>
	</n-form>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import {
	type FormInst,
	type FormValidationError,
	useMessage,
	type FormRules,
	NForm,
	NFormItem,
	NInput,
	NButton,
	NCheckbox
} from "naive-ui";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";

interface ModelType {
	email: string | null;
	password: string | null;
}

const router = useRouter();
const formRef = ref<FormInst | null>(null);
const message = useMessage();
const model = ref<ModelType>({
	email: null,
	password: null,
});

const rememberMe = ref(false);
const isSigningIn = ref(false); // Reactive variable for loading state

const emit = defineEmits<{
	(e: "forgot-password"): void;
}>();

const rules: FormRules = {
	email: [
		{
			required: true,
			trigger: ["blur"],
			message: "Email is required",
		}
	],
	password: [
		{
			required: true,
			trigger: ["blur"],
			message: "Password is required"
		}
	]
};

async function signIn(e: Event) {
	e.preventDefault();
	isSigningIn.value = true; // Start loading

	formRef.value?.validate(async (errors: Array<FormValidationError> | undefined) => {
		if (!errors) {
			try {
				await useAuthStore().fetchToken({
					email: model.value.email,
					password: model.value.password
				}, rememberMe.value);
				// check if there's redirect query
				const redirect = router.currentRoute.value.query.redirect;
				message.success("Successfully logged in");
				if (redirect) {
					router.push({ path: redirect as string, replace: true });
				} else {
					router.push({ path: "/", replace: true });
				}
			} catch (error: any) {
				if (error.response) {
					message.error(error.response.data.detail);
				} else {
					message.error("Something went wrong");
				}
			} finally {
				isSigningIn.value = false; // End loading
			}
		} else {
			message.error("Please fill in the required fields correctly");
			isSigningIn.value = false; // End loading
		}
	});
}
</script>
