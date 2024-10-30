import { renderIcon } from "@/utils"
import { h } from "vue"
import { RouterLink } from "vue-router"
import { type MenuMixedOption } from "naive-ui/es/menu/src/interface"

const DashboardIcon = "carbon:dashboard"
const TrafficDataIcon = "carbon:traffic-cone"
const PixelsIcon = "carbon:code"
// icon for distribution
const TrafficDistributionIcon = "carbon:fork"
const AffiliateIcon = "carbon:user-role"
const AdvertisingIcon = "carbon:customer-service"
const ReportIcon = "carbon:analytics"


export default function getItems(mode: "vertical" | "horizontal", collapsed: boolean): MenuMixedOption[] {
	return [
		{
			label: () => h(
				RouterLink,
				{
					to: {
						name: "Dashboard"
					}
				},
				{ default: () => "Dashboard" }
			),
			key: "/",
			icon: renderIcon(DashboardIcon),


		},
		{
			label: () => "Affiliates",
			key: "affiliates",
			icon: renderIcon(AffiliateIcon),
			children: [
				{
					label: () => h(
						RouterLink,
						{
							to: {
								name: "Affiliates"
							}
						},
						{ default: () => "Affiliates" }
					),
					key: "affiliates",
				},
				{
					label: "Pixels",
					key: "affiliates-pixels",
				},
				// postbacks
				{
					label: "Postbacks",
					key: "affiliates-postbacks",
				},
			]
		},

		{
			label: () => "Traffic Data",
			key: "traffic-data",
			icon: renderIcon(TrafficDataIcon),
			children: [
				{
					label: () => h(
						RouterLink,
						{
							to: {
								name: "Clicks"
							}
						},
						{ default: () => "Clicks" }
					),
					key: "clicks",
				},
				{
					label: "Leads",
					key: "leads",
				},
				{
					label: "Sales",
					key: "sales",
				}

			],
		},
		{
			label: () => "Pixels",
			key: "pixels-postbacks",
			icon: renderIcon(PixelsIcon),
			children: [
				{
					label: "Postbacks",
					key: "postbacks",
				},
				{
					label: "Pixels",
					key: "pixels",
				}
			],
		},
		{
			label: () => "Traffic Distribution",
			key: "traffic-distribution",
			icon: renderIcon(TrafficDistributionIcon),
			children: [
				{
					label: () => h(
						RouterLink,
						{
							to: {
								name: "AdvertisersList"
							}
						},
						{ default: () => "Advertisers" }
					),
					key: "traffic-distribution-advertisers",
				},
				{
					label: "Providers",
					key: "traffic-distribution",
				},
				{
					label: () => h(
						RouterLink,
						{
							to: {
								name: "RotationControl"
							}
						},
						{ default: () => "RotationControl" }
					),
					key: "rotation-control",
				}
			],
		},
		// reports - children: drill down report
		{
			label: () => "Reports",
			key: "reports",
			icon: renderIcon(ReportIcon),
			children: [
				{
					label: () => h(
						RouterLink,
						{
							to: {
								name: "DrillDown"
							}
						},
						{ default: () => "Drilldown Reports" }
					),
					key: "drill-down-report",
				},
			],
		},
	]
}
