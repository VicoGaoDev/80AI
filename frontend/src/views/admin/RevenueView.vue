<script setup lang="ts">
import { h, onMounted, ref } from "vue";
import { message, Modal } from "ant-design-vue";
import dayjs from "dayjs";
import type { Dayjs } from "dayjs";
import { AccountBookOutlined, BellOutlined } from "@ant-design/icons-vue";
import { getAdminAnalyticsPaymentRevenue, getAdminAnalyticsRedeemRevenue, testAdminDailyReportNotify } from "@/api/admin";
import { isSessionExpiredError } from "@/lib/authError";
import { useAuthStore } from "@/stores/auth";
import RedeemRevenueTable from "@/components/admin/RedeemRevenueTable.vue";
import type { AdminAnalyticsRedeemRevenue } from "@/types";

type DatePreset = "today" | "3d" | "7d" | "30d";

const auth = useAuthStore();
const loading = ref(false);
const sendingDailyReport = ref(false);
const preset = ref<DatePreset | undefined>("today");
const dateRange = ref<[Dayjs, Dayjs] | null>(null);
const redeemRevenue = ref<AdminAnalyticsRedeemRevenue | null>(null);
const paymentRevenue = ref<AdminAnalyticsRedeemRevenue | null>(null);

function formatQueryDate(value?: Dayjs) {
  return value ? value.format("YYYY-MM-DDTHH:mm:ss") : undefined;
}

function applyPreset(nextPreset: DatePreset) {
  const now = dayjs();
  preset.value = nextPreset;
  if (nextPreset === "today") {
    dateRange.value = [now.startOf("day"), now.endOf("day")];
    return;
  }
  if (nextPreset === "3d") {
    dateRange.value = [now.subtract(2, "day").startOf("day"), now.endOf("day")];
    return;
  }
  if (nextPreset === "7d") {
    dateRange.value = [now.subtract(6, "day").startOf("day"), now.endOf("day")];
    return;
  }
  dateRange.value = [now.subtract(29, "day").startOf("day"), now.endOf("day")];
}

function handlePresetChange(value: DatePreset) {
  applyPreset(value);
  load();
}

function handleDateRangeChange() {
  preset.value = undefined;
  if (dateRange.value?.[0] && dateRange.value?.[1]) {
    load();
  }
}

function handleReset() {
  applyPreset("today");
  load();
}

async function handleSendDailyReport() {
  sendingDailyReport.value = true;
  try {
    const result = await testAdminDailyReportNotify();
    message.success(result.sent ? "日报发送成功" : "日报未发送，请检查企业微信配置");
    Modal.info({
      title: "日报发送结果",
      width: 560,
      okText: "知道了",
      content: h("div", { class: "daily-report-result" }, [
        h("p", null, `发送状态：${result.sent ? "成功" : "未发送"}`),
        h("p", null, `报表日期：${result.report_date}`),
        h("p", null, `统计区间：${result.range_start} ~ ${result.range_end}`),
        h("p", null, `在线支付营业额：¥${Number(result.revenue_yuan || 0).toFixed(2)}`),
        h("p", null, `支付成功订单数：${result.paid_order_count}`),
        h("p", null, `兑换码营业额：¥${Number(result.redeem_revenue_yuan || 0).toFixed(2)}`),
        h("p", null, `兑换码使用次数：${result.redeem_used_count}`),
        h("p", null, `任务总数：${result.task_total_count}`),
        h("p", null, `成功任务数：${result.task_success_count}`),
        h("p", null, `失败任务数：${result.task_failed_count}`),
        h("p", null, `积分消耗：${result.credit_consumed}`),
      ]),
    });
  } catch (err: unknown) {
    if (isSessionExpiredError(err)) return;
    message.error((err as any)?.response?.data?.detail || "发送日报失败");
  } finally {
    sendingDailyReport.value = false;
  }
}

async function load() {
  if (!dateRange.value?.[0] || !dateRange.value?.[1]) {
    return;
  }
  loading.value = true;
  try {
    const query = {
      granularity: "day",
      start_date: formatQueryDate(dateRange.value[0].startOf("day")),
      end_date: formatQueryDate(dateRange.value[1].endOf("day")),
    } as const;
    const [redeemResult, paymentResult] = await Promise.all([
      getAdminAnalyticsRedeemRevenue(query),
      getAdminAnalyticsPaymentRevenue(query),
    ]);
    redeemRevenue.value = redeemResult;
    paymentRevenue.value = paymentResult;
  } catch (err: unknown) {
    if (isSessionExpiredError(err)) return;
    message.error("获取营业额数据失败");
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  applyPreset("today");
  load();
});
</script>

<template>
  <div class="warm-page motion-page-enter">
    <div class="warm-page-header motion-fade-up" style="--motion-delay: 40ms">
      <div class="warm-page-heading">
        <div class="warm-page-icon">
          <AccountBookOutlined />
        </div>
        <div>
          <div class="warm-page-title">营业额</div>
          <div class="warm-page-desc">统计在线购买与积分兑换码营业额，支持按时间区间筛选。</div>
        </div>
      </div>
      <a-button
        v-if="auth.isSuperAdmin"
        type="primary"
        class="warm-primary-btn revenue-header-btn"
        :loading="sendingDailyReport"
        @click="handleSendDailyReport"
      >
        <template #icon><BellOutlined /></template>
        发送日报到企业微信
      </a-button>
    </div>

    <div class="analytics-filter warm-card motion-fade-up motion-card-lift" style="--motion-delay: 120ms">
      <div class="analytics-filter-row">
        <a-range-picker
          v-model:value="dateRange"
          :placeholder="['开始日期', '结束日期']"
          class="analytics-filter-date"
          @change="handleDateRangeChange"
        />
        <div class="analytics-filter-panel-compact">
          <a-radio-group
            :value="preset"
            class="analytics-segmented-group analytics-segmented-group-secondary"
            button-style="solid"
            @update:value="handlePresetChange"
          >
            <a-radio-button value="today">今日</a-radio-button>
            <a-radio-button value="3d">近 3 天</a-radio-button>
            <a-radio-button value="7d">近 7 天</a-radio-button>
            <a-radio-button value="30d">近 30 天</a-radio-button>
          </a-radio-group>
        </div>
        <a-button type="primary" class="analytics-action-btn" :loading="loading" @click="load">查询</a-button>
        <a-button class="analytics-action-btn analytics-action-btn-secondary" @click="handleReset">重置</a-button>
      </div>
    </div>

    <div class="revenue-section-stack">
      <RedeemRevenueTable
        :data="paymentRevenue"
        :loading="loading"
        title="在线购买营业额"
        count-label="购买"
      />
      <RedeemRevenueTable
        :data="redeemRevenue"
        :loading="loading"
        title="兑换码营业额"
        count-label="兑换"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.analytics-filter {
  margin-bottom: 16px;
}

.revenue-section-stack {
  display: grid;
  gap: 16px;
}

.revenue-header-btn {
  min-width: 180px;
  margin-left: auto;
}

:deep(.daily-report-result) {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: var(--theme-text);

  p {
    margin: 0;
    line-height: 1.7;
  }
}

@media (max-width: 768px) {
  .analytics-filter-row {
    align-items: stretch;
  }

  .analytics-filter-date,
  .analytics-action-btn {
    width: 100%;
  }

  .revenue-header-btn {
    width: 100%;
    margin-left: 0;
  }
}
</style>
