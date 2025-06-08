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
        <div class="text-body-1 mb-4">This calculator uses Extreme Gradient Boosting, a powerful algorithm known for its accuracy and efficiency. XGBoost builds multiple decision trees sequentially, where each new tree corrects errors made by the previous ones. This makes it adept at capturing complex, non-linear relationships between patient features and the required arcuate sweep.</div>
        
        <div class="text-body-1 mb-4">The model incorporates a comprehensive set of patient-specific data to deliver personalized arcuate incision recommendations. By analyzing critical features such as corneal astigmatism, steep axis position, age, and anatomical measurements including white-to-white distance (WTW) and axial length (AL), the model accounts for the unique characteristics of each patient's eye. Additionally, the inclusion of age and prior LASIK history allows for further refinement of predictions. This data-rich approach, powered by XGBoost's advanced algorithms, enables the detection of subtle patterns and complex feature interactions that conventional nomograms typically overlook.</div>

        <div class="text-body-1 mb-4">The model has been specifically designed with a monotonic constraint on the astigmatism feature. This means that as corneal astigmatism increases, the recommended arcuate incision length will never decrease. This constraint ensures clinical relevance and predictability in surgical planning, as it aligns with the fundamental principle that higher degrees of astigmatism generally require more aggressive correction.</div>

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
          type="info"
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
  'Maximum AK sweep have been capped at 50 degrees. Based on our analysis, we believe that higher levels of astigmatism should be treated with toric lenses over laser AKs.',
  'The nomogram assumes a clear corneal temporal incision with a 2.4-2.8mm blade which can be assumed to create ~0.2 D of SIA at 180 deg. An "average" SIA has been captured by the weights during the machine learning process. Inputting a presumed SIA for an individual surgeon has not been shown to significantly improve results.',
  'The model treats low levels of anterior ATR astigmatism aggressively in order to mitigate the effects of posterior corneal astigmatism and known regression of treatment effect at these axes.',
  'The current iteration of this model was been trained using K readings and other measurements from the IOLMaster 700 (Zeiss Meditec).'
]
</script>

<style scoped>
.disclaimer-alert {
  background-color: #e3f2fd !important; /* Light blue */
  color: #1976d2 !important;           /* Dark blue text for contrast */
  border-left: 6px solid #bbdefb !important; /* Medium blue border */
}
</style>