# 数据汇总Banner

## 基础用法

:::demo
```vue
<template>
  <div class="summary-demo">
  <DataSummaryBanner :dataList="dataList">
    <template #default>
      <!-- 配置右侧操作按钮 -->
    </template>
  </DataSummaryBanner>
</div>
</template>
<style lang="less" scoped>
  .summary-demo {
    width: 1200px;
    margin-top: 20px;
  }
</style>
 <script setup>
  import DataSummaryBanner from '../../src/components/DataSummaryBanner.vue'
  import { nextTick, onMounted, ref } from 'vue'
  const dataList = ref([
    {
      label: 'SaaS服务数',
      value: '50',
      color: '#323233',
    },
    {
      label: '待生效',
      value: '0',
      color: '#0075BE'
    },
    {
      label: '生效中',
      value: '35',
      color: '#40C269'
    },
    {
      label: '即将到期',
      value: '12',
      color: '#F09918'
    },
    {
      label: '已失效',
      value: '3',
      color: '#F55858'
    },
    {
      label: '流失率',
      value: '6.5%',
      color: '#F55858'
    },
    {
      label: '已激活',
      value: '35',
      color: '#40C269'
    },
    {
      label: '未激活',
      value: '15',
      color: '#6E7EAA'
    },
    {
      label: '激活率',
      value: '70.5%',
      color: '#0075BE'
    }
  ])
</script>
```
:::
<style lang="less" scoped>
  .summary-demo {
    width: 1200px;
    margin-top: 20px;
  }
</style>

## 组件代码展示

```vue
<!-- 数据汇总横图 -->
<template>
  <div class="data-summary-banner">
    <div class="summary-config">
      <slot>
        <img src="https://res.ennew.com/image/png/87559d3e382f122692a6ea3f591bb2cc.png" alt="">
        <img src="https://res.ennew.com/image/png/20c2e255a050c2e3c6af200b76c24bd2.%E5%9B%BE%E6%A0%87%EF%BC%8F%E7%BA%BF%E6%80%A7%EF%BC%8F%E6%B7%BB%E5%8A%A0%402x%20(1).png" alt="">
      </slot>
    </div>
    <div class="summary-wrapper" v-if="props.dataList?.length">
      <div class="summary-item" v-for="(sub, subIndex) in props.dataList" :key="subIndex">
        <div class="item-label">{{ sub?.label }}</div>
        <div class="item-value" :style="{color: sub?.color}">{{ sub?.value }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  const props = defineProps({
    dataList: {
      type: Array,
      default: () => []
    }
  })
</script>

<style scoped lang="less">
  .data-summary-banner {
    width: 100%;
    border: 1px solid #FFFFFF;
    background-color: #F3FAFE;
    .summary-config {
      padding: 13px 17px 0 0;
      display: flex;
      justify-content: flex-end;
      > img {
        width: 14px;
        height: 14px;
        margin-right: 14px;
        &:last-child {
          margin-right: 0;
        }
      }
    }
    .summary-wrapper {
      padding: 0 144px 27px 23px; 
      display: flex;
      width: 100%;
    }
    .summary-item {
      display: flex;
      flex: 1;
      flex-direction: column;
      margin-right: 46px;
      position: relative;
      white-space: nowrap;
      &:nth-child(1) {
        padding-right: 40px;
        &::after {
          content: "";
          position: absolute;
          right: 0px;
          top: 0;
          bottom: 4px;
          width: 1px;
          background-color: #C8C9CC;
        }
      }
      &:nth-child(6) {
        padding-right: 40px;
        &::after {
          content: "";
          position: absolute;
          right: 0px;
          top: 0;
          bottom: 4px;
          width: 1px;
          background-color: #C8C9CC;
        }
      }
      .item-label {
        font-family: PingFang SC, PingFang SC;
        font-weight: 500;
        font-size: 14px;
        color: #646566;
        line-height: 16px;
      }
      .item-value {
        font-family: D-DIN-PRO, D-DIN-PRO;
        font-weight: bold;
        font-size: 24px;
        color: #323233;
        line-height: 32px;
        margin-top: 6px;
      }
      .summary-divider {
        height: 100%;
        width: 1px;
        background-color: #C8C9CC;
        margin: 0 40px;
      }
    }
  }
</style>

```


## 带饼图统计汇总
:::demo
```vue
<template>
  <div class="banner-wrap">
    <div class="pie-row-container" v-for="(it, i) in data" :key="i">
      <div  class="chart-title">{{ it.title }}</div>
      <div class="flex-y-center">
        <div class="pie-container">
          <div ref="chartRef" class="pie-wrap"></div>
        </div>
        <div class="total-wrap">
          <div class="total">
            {{ it.total || '-' }}
          </div>
          <div class="total-label">总计</div>
        </div>
        <div
            class="pie-data-wrap flex-grow"
        >
          <div v-for="(item, i) in it.list" :key="item.name" class="item">
            <div class="vertical-line" :style="{ background: item.color }"></div>
            <div>
              <div class="name">{{ item.name }}</div>
              <div class="value bold">
                {{ item.value ?? '-' }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { nextTick, onMounted, ref, computed } from 'vue'
import * as echarts from 'echarts';

const data = ref([
  {
    title: '责令改正类型统计',
    total: 0,
    list: [
      { name: '立即整改', value: 2, color: 'rgba(224, 19, 57, 1)' },
      { name: '限期整改', value: 2, color: 'rgba(253, 207, 44, 1)' },
      { name: '停产停业', value: 1, color: 'rgba(255, 122, 0, 1)' },
    ]
  },
  {
    title: '责令改改正处置状态统计',
    total: 0,
    list: [
      { name: '待查看', value: 2, color: 'rgba(255, 214, 0, 1)' },
      { name: '已查看', value: 2, color: 'rgba(0, 134, 255, 1)' },
    ]
  }
])

const chartRef = ref()
const total = ref(0)
const getOption = (list) => {
  return ({
    title: {
      show: false
    },
    tooltip: {
      trigger: 'item',
      position: 'right',
      formatter: (params) => {
        return `${params.marker} <span style="display: inline-block;margin-right: 20px;">${params.name}</span>${
            params.value
        }`;
      }
    },
    legend: {
      show: false
    },
    series: [
      {
        type: 'pie',
        radius: ['68%', '88%'],
        labelLine: {
          show: false
        },
        emphasis: {
          scale: true,
          scaleSize: 3,
          itemStyle: {
            color: 'inherit'
          }
        },
        label: {
          normal: {
            show: false,
          }
        },
        itemStyle: {
          color: function (params) {
            return params.data.color;
          }
        },
        silent: false,
        data: list
      }
    ]
  })
};
const init = (d, ele) => {
  d.total = d.list.reduce((acc = 0, cur) => acc + cur.value, 0);
  const option = getOption(d.list)
  const myChart = echarts.init(ele);
  myChart.setOption(option);
};
onMounted(() => {
  nextTick(() => {

    // 初始化饼图
    const chartEle = document.getElementsByClassName('pie-wrap');
    Array.from(chartEle)?.forEach((ele, index) => {
      init(data.value[index], ele)
    })
  })
});
</script>
<style lang="less" scoped>
  .banner-wrap {
    background: linear-gradient( 161deg, #DEEBFF 2%, #F6FAFF 59%, #FAFBFF 100%);
    padding: 20px;
    min-width: 1180px;
    display: flex;
  }
  .pie-row-container {
    &:not(:last-of-type) {
      margin-right: 34px;
    }
  }
  .pie-container {
    margin-right: 16px;
    flex-shrink: 0;
  }
  .chart-title {
    font-size: 16px;
    color: rgba(24, 31, 67, 0.60);
    line-height: 22px;
    font-weight: bold;
    margin-bottom: 8px;
  }
  .pie-wrap {
    width: 80px;
    height: 80px;
  }
  .total-wrap {
    margin-right: 46px;
  }
  .total {
    font-weight: bold;
    font-size: 36px;
    color: #181F43;
    line-height: 44px;
  }
  .total-label {
    font-weight: 400;
    font-size: 14px;
    color: rgba(24,31,67,0.6);
    line-height: 22px;
  }
  .pie-data-wrap {
    display: flex;
    > .item {
      display: flex;
      margin-right: 32px;
    }
  }
  .vertical-line {
    width: 2px;
    height: 14px;
    margin-top: 4px;
    margin-right: 10px;
    flex-shrink: 0;
  }
  .name {
    color:rgba(24, 31, 67, 0.60);
    font-size: 14px;
    line-height: 22px;
    flex-shrink: 0;
  }
  .value {
    color: rgba(24, 31, 67, 1);
    font-size: 20px;
    line-height: 32px;
    flex-shrink: 0;
  }
  .flext-grow {
    flex-grow: 1;
  }
  .flex-y-center {
    display: flex;
    align-items: center;
  }
  .bold {
    font-weight: bold;
  }
</style>
```
:::
<br>
<br>
