<template>
  <v-container>
    <v-row>
      <v-col>
        <div class="text-h3 font-weight-medium mb-6">About De Rojas AI Calc</div>

        <div class="text-h5 font-weight-medium mb-3">Background</div>
        <div class="text-body-1 mb-4"><strong>Arcuate incisions ("AIs")</strong>, also known as arcuate keratotomies, are used during cataract surgery to correct astigmatism. They are a powerful tool, but there is limited medical consensus on how to best employ them, how to create them (e.g., via femtosecond laser/"FLACS" or manually with diamond blades?), or how to fine-tune them for specific levels of astigmatism or patient characteristics.</div>
        <div class="text-body-1 mb-4">The author has extensive experience using precisely-placed femtosecond laser-created AIs to improve visual outcomes for his patients.</div>

        <div class="text-body-1 mb-4">Multiple published models nomograms exist to help guide surgeons on incision parameters (sweep length and axis). Links to some prior published nomograms are available in the "Other Resources" menu at the top of the webpage.</div>

        <div class="text-h5 font-weight-medium mb-3 mt-5">The Model</div>
        <div class="text-body-1 mb-4">The De Rojas AI Calc model has been developed using machine learning and has been trained and validated on hundreds of FLACS cases performed by experienced surgeons.</div>
        
        <div class="text-h5 font-weight-medium mb-3 mt-5">About the machine learning model:</div>
        <div class="text-body-1 mb-4">This calculator uses XGBoost (Extreme Gradient Boosting), a powerful algorithm known for its accuracy and efficiency. XGBoost builds multiple decision trees sequentially, where each new tree corrects errors made by the previous ones. This makes it adept at capturing complex, non-linear relationships between patient features and the required arcuate sweep.</div>
        
        <div class="text-body-1 mb-4">Unlike many traditional nomograms that primarily rely on astigmatism magnitude and possibly age, our model incorporates a richer set of patient data. Features such as laterality (OD/OS), white-to-white distance (WTW), average keratometry (Mean K), axial length (AL), and prior LASIK status, in addition to age and astigmatism details (magnitude and axis), allow the model to learn more nuanced patterns and provide more personalized predictions. The use of XGBoost enables the deciphering of complex interactions between these features that simpler models might miss.</div>

        <div class="text-h5 font-weight-medium mb-3 mt-5">Model Assumptions</div>
        <div class="text-body-1 mb-4">The model was trained with the following assumptions:</div>
        <div class="text-body-1 mb-4">
          <ul class="pl-4">
            <li v-for="(item, i) in assumptions" :key="i" class="mb-2">
              {{ item }}
            </li>
          </ul>
        </div>

        <div class="text-h5 font-weight-medium mb-3 mt-5">Future Development</div>
        <div class="text-body-1 mb-4">Please note that these models are currently in BETA. The author plans to create updated, customizable versions of this model. Future iterations may allow retraining based on user-submitted datasets with post-operative outcomes.</div>

        <div class="text-h5 font-weight-medium mb-3 mt-5">Disclaimer</div>
        <v-alert
          type="warning"
          class="mb-4 disclaimer-alert"
          elevation="2"
        >
          This web application is intended for investigational purposes only. It is not approved to guide surgical correction of astigmatism in humans.
        </v-alert>

        <div class="text-h5 font-weight-medium mb-3 mt-5">Contact</div>
        <div class="text-body-1 d-flex align-center mb-6">
          Please feel free to email the author with any questions or concerns:
          <v-btn
            href="mailto:joaquin.derojas@gmail.com"
            variant="text"
            class="text-primary pa-0 text-decoration-underline text-none ms-1"
            style="height: auto;"
          >
          joaquin.derojas@gmail.com
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
const assumptions = [
  'The ALLY® Robotic Cataract Laser System (LENSAR, Inc) is used to make laser arcuate keratotomies (AKs).',
  'AKs are made at 80% depth.',
  'AKs are made at 4.5mm radius from the visual center.',
  'All AKs were opened and irrigated at the time of surgery with a BSS cannula.',
  'We do not recommend treating very low levels of astigmatism (< 0.25 D) with AKs.',
  'Maximum AK sweep have been capped at 50 degrees. It is our opinion that higher levels of astigmatism should be treated with toric lenses over laser AKs.',
  'The nomogram assumes a clear corneal temporal incision with a 2.4-2.8mm blade which can be assumed to create ~0.2 D of SIA at 180 deg. An "average" SIA has been captured by the weights during the machine learning process. Inputting a presumed SIA for an individual surgeon has not been shown to significantly improve results.',
  'The current iteration of this model was been trained using K readings and other measurements from the IOLMaster 700 (Zeiss Meditec).'
]
</script>

<style scoped>
.disclaimer-alert {
  background-color: #fff3e0 !important; /* Light orange */
  color: #ef6c00 !important;           /* Dark orange text for contrast */
  border-left: 6px solid #ffe0b2 !important; /* Slightly darker orange border */
}
</style>