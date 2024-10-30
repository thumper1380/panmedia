import dayjs from "dayjs"
import timezone from "dayjs/plugin/timezone"
import utc from 'dayjs/plugin/utc';
import locale_en from "dayjs/locale/en.js"
import customParseFormat from "dayjs/plugin/customParseFormat"
import relativeTime from "dayjs/plugin/relativeTime"

/*
import isSameOrAfter from "dayjs/plugin/isSameOrAfter"
import utc from "dayjs/plugin/utc"
import duration from "dayjs/plugin/duration"
dayjs.extend(isSameOrAfter)
dayjs.extend(utc)
dayjs.extend(duration)
*/
dayjs.extend(relativeTime)
dayjs.extend(customParseFormat)
dayjs.extend(timezone)
dayjs.extend(utc)
dayjs.locale(locale_en)
dayjs.tz.setDefault(dayjs.tz.guess())

export default dayjs

export const toRelativeTime = (datetime: string) => {
    return dayjs(datetime).fromNow();
  };