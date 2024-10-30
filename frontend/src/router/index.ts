import { createRouter, createWebHistory } from "vue-router"
import { Layout } from "@/types/theme.d"
import { authCheck } from "@/utils/auth"


const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: "/",
			name: "Dashboard",
			component: () => import("@/views/Dashboard.vue"),
			meta: { title: "Dashboard", auth: true, roles: "all" }
		},
		{
			path: "/profile",
			name: "Profile",
			component: () => import("@/views/Profile.vue"),
			meta: { title: "Profile", auth: true, roles: "all" }
		},
		{
			path: "/trafficdata/clicks",
			name: "Clicks",
			props: true,
			component: () => import("@/views/TrafficData/Clicks.vue"),
			meta: { title: "Clicks", auth: true, roles: "all" }
		},
		{
			path: "/clicks/:id",
			name: "ClicksDetails",
			props: true,
			component: () => import("@/views/TrafficData/DetailView.vue"),
			meta: { title: "Clicks", auth: true, roles: "all" }
		},
		{
			path: "/affiliates",
			name: "Affiliates",
			component: () => import("@/views/Affiliate/AffiliateListView.vue"),
			meta: { title: "Affiliates", auth: true, roles: "all" }
		},
		{
			path: "/affiliates/:id",
			name: "AffiliateDetails",
			props: true,
			component: () => import("@/views/Affiliate/AffiliateDetailView.vue"),
		},
		{
			path: "/advertisers",
			name: "AdvertisersList",
			component: () => import("@/views/Advertiser/AdvertiserListView.vue"),
			meta: { title: "Advertisers", auth: true, roles: "all" }
		},
		{
			path: '/advertisers/:id',
			name: 'AdvertiserDetails',
			props: true,
			component: () => import("@/views/Advertiser/AdvertiserDetailView.vue"),
		},
		{
			path: "/rotation-control",
			name: "RotationControl",
			component: () => import("@/views/TrafficDistribution/RotationControl.vue"),
			meta: { title: "Rotation Control", auth: true, roles: "all" }
		},
		{
			path: "/reports/drilldown",
			name: "DrillDown",
			component: () => import("@/views/Reports/DrillDownReport.vue"),
			meta: { title: "Drilldown Reports", auth: true, roles: "all" }
		},
		{
			path: "/login/:redirect?",
			name: "Login",
			component: () => import("@/views/Auth/Login.vue"),
			meta: { title: "Login", forceLayout: Layout.Blank, checkAuth: true }
		},
		{
			path: "/logout",
			name: "Logout",
			redirect: "/login"
		},
		{
			path: "/:pathMatch(.*)*",
			name: "NotFound",
			component: () => import("@/views/NotFound.vue"),
			meta: { forceLayout: Layout.Blank }
		},

	],
	scrollBehavior(to, from, savedPosition) {
		if (savedPosition) {
			return savedPosition
		} else {
			return { top: 0 }
		}
	},
	sensitive: true,
})


// process is not defined in vite, so we need to use import.meta.env
router.beforeEach(route => {
	const appName = import.meta.env.VITE_APP_NAME
	// title | appName
	document.title = route.meta.title ? `${appName} | ${route.meta.title}` : appName
	return authCheck(route)
})

export default router
