import { h } from "vue";
import { type TrafficData } from "@/types/trafficdata";
import dayjs from "@/utils/dayjs";
import { RouterLink } from "vue-router";
import Icon from "@/components/common/Icon.vue";
import { NIconWrapper, NPopover, NTag, NSkeleton } from "naive-ui";
import ColorTag from "@/components/ColorTag.vue";
import { FieldType, type Column } from "@/types/response";



// helper function to retrieve RelatedField column ...Details route name
const getRelatedFieldRouteName = (key: string): string => {
    switch (key) {
        case 'affiliate':
            return 'AffiliateDetails';
        case 'funnel':
            return 'FunnelDetails';
        case 'advertiser':
            return 'AdvertiserDetails';
        case 'auto_login':
            return 'AutoLoginDetails';
        case 'source':
            return 'SourceDetails';
        default:
            return '';
    }
};




function showSkeleton() {
    return h(NSkeleton, {
        animated: false,
        round: true,
        // circle: true,
        text: true,
        sharp: true,
        repeat: 1,
        width: '70%',
    });
}


const renderColumn = (view: string | null, row: any, column: Column): ReturnType<typeof h> => {
    const value = row[column.key];
    column.maxWidth = 400;
    column.minWidth = 50;
    column.resizable = true;

    // check if row is empty json object
    if (Object.keys(row).length === 0 && row.constructor === Object) {
        return showSkeleton();
    }
    switch (column.type) {
        case FieldType.IDField:
            if (view) {
                column.width = 70;
                return h(RouterLink, {
                    to: {
                        name: view,
                        params: {
                            id: row.id
                        }
                    }
                }, () => row.id);
            }
        case FieldType.CharField:
            column.width = 150;

            return h('div', {}, value);
        case FieldType.CountryField:
            column.width = 100

            return h('div',
                {
                    style: {
                        display: 'flex',
                        alignItems: 'center' // This will vertically center the icon and text
                    },
                },
                [
                    h(Icon, {
                        name: `circle-flags:${String(value).toLowerCase()}`, // Convert value to string before calling toLowerCase()
                        size: 15
                    }),
                    h('span', { style: 'margin-left: 10px;' }, `${String(value.toUpperCase())}`)
                ]
            )
        case FieldType.RelatedField:
            if (!value) {
                return h('span', 'N/A');
            }
            column.width = 170;
            return h(RouterLink, {
                to: {
                    name: getRelatedFieldRouteName(column.key),
                    params: {
                        id: value.id
                    }
                }
            }, () => value.name);
        case FieldType.TagField:
            // let color = statusConf.value.find(status => status.name === value)?.color;
            // return h(ColorTag, { color: '#eff', text: value });
            column.width = 150;
            return h('div', {}, value);


        case FieldType.StateField:
            column.width = 150;
            return h('div',
                {
                    style: {
                        display: 'flex',
                        alignItems: 'center' // This will vertically center the icon and text

                    },
                },
                [
                    h(NIconWrapper, {
                        size: 8,
                        borderRadius: 50,
                        // iconColor: 
                        // color: saleStatusesConf.value.find(status => status.name === row[column.key])?.color,
                    }),
                    [
                        h('span', { style: 'margin-left: 5px; font-size: 1rem;' }, `${String(value)}`),
                    ]
                ]
            )

        case FieldType.DateTimeField:
            column.width = 250;
            column.resizable = true;
            const date = new Date(value);
            // days since
            const timeSince = dayjs(date).fromNow();
            // return h('span', new Date(value).toLocaleString());
            // represent date, and use popover to show since
            return h(NPopover, {
                trigger: 'hover',
                duration: 0,
                delay: 50,
                placement: 'left',
            }, {
                default: () => h('span', timeSince),
                trigger: () => h('span', date.toLocaleString()),
            });




        case FieldType.BooleanField:
            column.width = 90;
            return h(Icon, {
                name: value ? 'carbon:checkmark' : 'carbon:close',
                size: 16,
                color: value ? '#00b27b' : '#ff0156',
            });


        case FieldType.StatusField:
            column.width = 100;
            return h(NTag, {
                type: value ? 'success' : 'error',
                size: 'small',
            }, { default: () => value ? 'Active' : 'Inactive' })



        default:
            console.log(row, column);
            return h('div', {}, value);
    }
};


export default renderColumn;