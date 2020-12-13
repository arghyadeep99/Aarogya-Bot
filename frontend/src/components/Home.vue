<template>
  <div class="grid">
    <div class="main">
      <h1>
        Aarogya Bot
        <span class="underlines">
          <span class="underline" style="margin-left: 0%"></span>
          <span class="underline" style="margin-left: 25%"></span>
          <span class="underline" style="margin-left: 50%"></span>
          <span class="underline" style="margin-left: 75%"></span>
        </span>
      </h1>

      <p class="subtitle">
        Submission for HackOff-3.0 Siemens Healthineers Problem Statement on
        Medical Chatbot
      </p>

      <h2 style="margin-top: 1em">About</h2>
      <p style="margin-top: 0.5em">
        Aarogya Bot is an AI-driven chatbot that will help you answer your basic
        medical queries, amidst the Covid-19 pandemic, where moving out to
        consult a doctor isn't a luxury anymore. The chatbot can respond to your
        medical queries only to the best of its knowledge graph base, so be
        mindful of that and always cross check the responses of Aarogya Bot with
        a medical professional!
      </p>

      <h2 style="margin-top: 1em">Problem it solves</h2>
      <p style="margin-top: 0.5em">
        Today, as the world faces the Covid-19 Pandemic, the world has entered
        lockdown mode, with partial lockdown varying across demography. People
        are confused about a lot of things and wish to consult medical
        professional advice. However, lockdown restricts this luxury and hence
        it becomes very convenient to have a chatbot that can answer your basic
        medical queries.
      </p>
      <p style="margin-top: 0.5em">
        Aarogya Bot can attempt to answer your queries about a limited set of
        diseases as of now. It can tell you about its symptoms, precaution and
        description of the disease. In case it can't answer your queries, or if
        you feel unsatisfied by the response, you are strongly adviced to
        consult a medical professional. Since this is a vanilla implementation
        of our chatbot, we strongly advice against blind faith in the responses.
      </p>

      <h2 style="margin-top: 1em">Problem it solves</h2>
      <p style="margin-top: 0.5em">
        We have built a knowledge graph database of selected diseases, their
        symptoms, precautions and description. These relationships are stored in
        a Neo4j database, from where the results can be fetched.
      </p>
      <p style="margin-top: 0.5em">
        To understand user query, we make use of Aho-Corasick algorithm, to
        identify the patterns of type of question asked and fetch suitable
        results.
      </p>
      <p style="margin-top: 0.5em">
        Our Neo4j database is queried, and the appropriate result is returned to
        the user.
      </p>
      <p style="margin-top: 0.5em">
        In case a question isn't found in our knowledge graph, we make use of
        question-answer pairs derived from https://questiondoctors.com and use
        Question Similarity to see most probable question that matches the user
        query and return the answer correpsonding to that question.
      </p>
      <p style="margin-top: 0.5em">
        For Question Similarity, we initially tried Bidirectional LSTM +
        Attention model, but we were having problems trying to use it as a
        predictor function. So, we now use Siamese-LSTM to make our predictions
        for most probable question. Datasetused was Quora-Question-Similarity,
        hosted on Kaggle.
      </p>
      <p style="margin-top: 0.5em">
        The result fetched through question-similarity method may not aalways be
        most apt, since a completely unrelated question, still may match with
        some queries from our dataset, based on similarity score. We look
        forward to improve this segment of our chatbot in future.
      </p>
    </div>
    <div></div>
  </div>
</template>

<script>
export default {};
</script>

<style scoped>
@import "../assets/style.css";
</style>