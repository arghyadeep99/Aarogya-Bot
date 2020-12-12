<template>
  <div id="app">
    <h1>Aarogya Bot</h1>
    <VueBotUI
      :messages="data"
      :options="botOptions"
      @msg-send="messageSendHandler"
    />
  </div>
</template>

<script>
import { VueBotUI } from 'vue-bot-ui'

export default {
  name: 'App',
  components: {
    VueBotUI
  },
  data(){
    return{
      data: [],
      botOptions:{
        botTitle: 'Aarogya Bot'
      }
    }
  }
}
</script>

<style>

</style>
