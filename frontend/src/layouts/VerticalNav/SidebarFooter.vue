<template>
	<div class="sidebar-footer" :class="{ collapsed }">
		<n-menu :options="menuOptions" :collapsed="collapsed" :collapsed-width="collapsedWidth" />
	</div>
</template>

<script lang="ts" setup>
import { computed, h, ref, toRefs } from "vue"
import { NMenu } from "naive-ui"
import { useThemeStore } from "@/stores/theme"
import { renderIcon } from "@/utils"
import { RouterLink } from "vue-router"

const ProfileIcon = "ion:person-circle-outline"
const SettingsIcon = "ion:settings-outline"

defineOptions({
	name: "SidebarFooter"
})
const props = withDefaults(
	defineProps<{
		collapsed?: boolean
	}>(),
	{ collapsed: false }
)
const { collapsed } = toRefs(props)

const menuOptions = ref([
	{
		label: () => h(
			RouterLink,
			{
				to: {
					name: "Profile"
				}
			},
			{ default: () => "Profile" }
		),
		key: 'profile',
		icon: renderIcon(ProfileIcon),
	},
	{
		label: 'Settings',
		key: 'settings',
		icon: renderIcon(SettingsIcon),
	}
])

const collapsedWidth = computed<number>(() => useThemeStore().sidebar.closeWidth - 16)
</script>

<style lang="scss" scoped>
.sidebar-footer {
	margin: 8px;
	background-color: var(--bg-body);
	border-radius: var(--border-radius);
	padding: 3px 0;
	transition: all 0.3s;

	:deep() {
		.n-menu {
			.n-menu-item-content.n-menu-item-content--selected::before {
				background-color: transparent !important;
			}
		}
	}
}
</style>
