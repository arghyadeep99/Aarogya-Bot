<template>
  <div id="app">
    <h1>Aarogya Bot</h1>
    <VueBotUI
      :messages="messages"
      :options="botOptions"
      :bot-typing="botTyping"
      @msg-send="messageSendHandler"
    />
  </div>
</template>

<script>
import axios from "axios";
import { VueBotUI } from "vue-bot-ui";

export default {
  name: "App",
  components: {
    VueBotUI,
  },
  data() {
    return {
      messages: [],
      botTyping: false,
      botOptions: {
        botTitle: "Aarogya Bot",
      },
    };
  },
  methods: {
    messageSendHandler(value) {
      this.messages.push({
        agent: "user",
        type: "text",
        text: value.text,
      });

      this.botTyping = true;

      axios.get("http://localhost:5000/?search=" + value.text).then((res) => {
        console.log(res);

        this.messages.push({
          agent: "bot",
          type: "text",
          text: res.data.message,
        });

        this.botTyping = false;
      });
    },
  },
};
</script>

<style>
</style>
