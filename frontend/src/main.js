import './style.css'

const API = 'http://127.0.0.1:8000'

document.querySelector('#app').innerHTML = `
  <div class="app">

    <header class="header">
      <div>
        <h1>AI Risk Manager</h1>
        <p>Defensive AI for fraud, chargebacks and payment risk</p>
      </div>

      <div class="status">
        <span class="status-dot"></span>
        System Online
      </div>
    </header>

    <main class="container">

      <section class="hero">
        <span class="badge">RISK INTELLIGENCE</span>

        <h2>
          Protect every transaction
          <br>
          with explainable AI
        </h2>

        <p>
          Analyze transaction behavior, merchant risk and
          fraud signals before money is lost.
        </p>
      </section>

      <section class="cards">

        <div class="metric">
          <span>Total Transactions</span>
          <strong>30,000</strong>
          <small>Monitored</small>
        </div>

        <div class="metric">
          <span>High Risk</span>
          <strong>1,842</strong>
          <small>Requires review</small>
        </div>

        <div class="metric">
          <span>Fraud Rate</span>
          <strong>4.8%</strong>
          <small>Current dataset</small>
        </div>

        <div class="metric">
          <span>Active Alerts</span>
          <strong id="alertCount">0</strong>
          <small>Fraud spikes</small>
        </div>

      </section>

      <section class="grid">

        <div class="panel">

          <div class="panel-title">
            <div>
              <h3>Transaction Analyzer</h3>
              <p>Evaluate a payment in real time</p>
            </div>

            <span class="ai-badge">AI</span>
          </div>

          <div class="form-grid">

            <label>
              Transaction Amount
              <input id="amount" type="number" value="75000">
            </label>

            <label>
              Payment Method
              <select id="payment_method">
                <option>CARD</option>
                <option>UPI</option>
                <option>NETBANKING</option>
                <option>WALLET</option>
              </select>
            </label>

            <label>
              Merchant Category
              <select id="merchant_category">
                <option>Electronics</option>
                <option>Fashion</option>
                <option>Travel</option>
                <option>Food</option>
                <option>Gaming</option>
              </select>
            </label>

            <label>
              Average Transaction
              <input id="avg_transaction_amount" type="number" value="2500">
            </label>

            <label>
              New Device
              <select id="is_new_device">
                <option value="1">Yes</option>
                <option value="0">No</option>
              </select>
            </label>

            <label>
              IP Risk Score
              <input id="ip_risk_score" type="number"
                     step="0.01" min="0" max="1" value="0.85">
            </label>

            <label>
              Transactions / Hour
              <input id="transactions_last_1h" type="number" value="7">
            </label>

            <label>
              Failed Attempts
              <input id="failed_attempts_last_24h" type="number" value="5">
            </label>

          </div>

          <button id="analyzeButton" class="analyze">
            Analyze Transaction →
          </button>

        </div>

        <div class="panel">

          <div class="panel-title">
            <div>
              <h3>Risk Decision</h3>
              <p>Explainable AI assessment</p>
            </div>
          </div>

          <div id="result" class="empty">
            <div class="empty-icon">AI</div>

            <p>
              Submit a transaction to generate
              a risk assessment.
            </p>
          </div>

        </div>

      </section>

      <section class="panel performance">

        <div class="panel-title">

          <div>
            <h3>AI Model Performance</h3>
            <p>Evaluated using held-out validation data</p>
          </div>

          <span class="ai-badge">
            VERIFIED METRICS
          </span>

        </div>

        <div id="metrics" class="performance-grid">
          <div class="loading">
            Loading model metrics...
          </div>
        </div>

      </section>

      <section class="panel">

        <div class="panel-title">

          <div>
            <h3>Fraud Spike Monitoring</h3>
            <p>Detect unusual increases in fraud activity</p>
          </div>

          <button id="refreshAlerts" class="secondary">
            Refresh Alerts
          </button>

        </div>

        <div id="alerts" class="no-alerts">
          No active fraud spike alerts detected.
        </div>

      </section>

      <footer>
        <span>AI Risk Manager</span>

        <span>
          Defensive fraud prevention • Explainable AI
        </span>
      </footer>

    </main>

  </div>
`

function getValue(id) {
  return document.querySelector(`#${id}`).value
}

function getNumber(id) {
  return Number(getValue(id))
}

function riskClass(level) {

  if (!level) return 'low'

  return level.toLowerCase()
}

async function analyzeTransaction() {

  const button =
    document.querySelector('#analyzeButton')

  const result =
    document.querySelector('#result')

  button.disabled = true
  button.textContent = 'Analyzing...'

  try {

    const transaction = {

      amount: getNumber('amount'),

      payment_method:
        getValue('payment_method'),

      merchant_category:
        getValue('merchant_category'),

      customer_account_age_days: 120,

      is_new_device:
        getNumber('is_new_device'),

      ip_risk_score:
        getNumber('ip_risk_score'),

      location: 'Mumbai',

      distance_from_usual_location: 450,

      failed_attempts_last_24h:
        getNumber('failed_attempts_last_24h'),

      transactions_last_1h:
        getNumber('transactions_last_1h'),

      transactions_last_24h: 15,

      avg_transaction_amount:
        getNumber('avg_transaction_amount'),

      transaction_amount_deviation: 30,

      previous_chargebacks: 1,

      previous_fraud_flags: 1,

      merchant_risk_score: 0.72,

      account_velocity: 0.47,

      hour_of_day: 3,

      day_of_week: 2
    }

    const response = await fetch(
      `${API}/transactions/risk-decision`,
      {
        method: 'POST',

        headers: {
          'Content-Type': 'application/json'
        },

        body: JSON.stringify(transaction)
      }
    )

    const data = await response.json()

    if (!response.ok) {
      throw new Error(
        data.detail || 'Risk analysis failed'
      )
    }

    const decision =
      data.risk_decision || data

    displayResult(decision)

  } catch (error) {

    result.innerHTML = `
      <div class="error">
        <strong>Risk analysis failed</strong>
        <p>${error.message}</p>
      </div>
    `

  } finally {

    button.disabled = false
    button.textContent =
      'Analyze Transaction →'
  }
}


function displayResult(data) {

  const result =
    document.querySelector('#result')

  const level =
    data.risk_level || 'UNKNOWN'

  const score =
    data.final_risk_score ?? 0

  const decision =
    data.decision || 'REVIEW'

  const breakdown =
    data.signal_breakdown || {}

  const reasons =
    data.reasons || []

  result.innerHTML = `

    <div class="risk-score">

      <div class="score ${riskClass(level)}">
        ${score}
      </div>

      <div>
        <span>Risk Score</span>

        <h2>${level}</h2>

        <strong>${decision}</strong>
      </div>

    </div>

    <div class="signals">

      <div>
        <span>ML Score</span>
        <strong>
          ${breakdown.ml_score ?? '-'}
        </strong>
      </div>

      <div>
        <span>Behavior</span>
        <strong>
          ${breakdown.behavioral_score ?? '-'}
        </strong>
      </div>

      <div>
        <span>Merchant</span>
        <strong>
          ${breakdown.merchant_score ?? '-'}
        </strong>
      </div>

    </div>

    <div class="reasons">

      <h4>Why was this flagged?</h4>

      <ul>

        ${
          reasons.length
            ? reasons.map(
                reason => `<li>${reason}</li>`
              ).join('')
            : '<li>No specific reasons returned.</li>'
        }

      </ul>

    </div>
  `
}


async function loadMetrics() {

  const container =
    document.querySelector('#metrics')

  try {

    const response =
      await fetch(`${API}/model/metrics`)

    const metrics =
      await response.json()

    if (metrics.error) {
      throw new Error(metrics.error)
    }

    container.innerHTML = `

      <div class="performance-card">
        <span>Precision</span>

        <strong>
          ${(metrics.precision * 100).toFixed(1)}%
        </strong>

        <small>
          Correct positive predictions
        </small>
      </div>

      <div class="performance-card">
        <span>Recall</span>

        <strong>
          ${(metrics.recall * 100).toFixed(1)}%
        </strong>

        <small>
          Risk cases successfully detected
        </small>
      </div>

      <div class="performance-card">
        <span>F1 Score</span>

        <strong>
          ${(metrics.f1 * 100).toFixed(1)}%
        </strong>

        <small>
          Precision and recall balance
        </small>
      </div>

      <div class="performance-card">
        <span>Threshold</span>

        <strong>
          ${metrics.threshold}
        </strong>

        <small>
          Validation-selected threshold
        </small>
      </div>
    `

  } catch (error) {

    container.innerHTML = `
      <div class="error">
        Unable to load model metrics:
        ${error.message}
      </div>
    `
  }
}


async function loadFraudSpikes() {

  const alerts =
    document.querySelector('#alerts')

  try {

    const response =
      await fetch(`${API}/fraud-spikes`)

    const data =
      await response.json()

    const items =
      data.alerts || []

    document.querySelector('#alertCount')
      .textContent = items.length

    if (!items.length) {

      alerts.innerHTML =
        'No active fraud spike alerts detected.'

      alerts.className =
        'no-alerts'

      return
    }

    alerts.className =
      'alert-list'

    alerts.innerHTML =
      items.map(
        spike => `
          <div class="alert">

            <div class="alert-icon">
              !
            </div>

            <div class="alert-content">

              <strong>
                ${spike.severity || 'HIGH'}
              </strong>

              <h4>
                ${spike.merchant_category || 'Unknown'}
              </h4>

              <p>
                Fraud spike detected.
              </p>

            </div>

            <div class="multiplier">
              ${spike.spike_multiplier || '-'}x

              <span>
                baseline
              </span>
            </div>

          </div>
        `
      ).join('')

  } catch (error) {

    alerts.innerHTML = `
      Unable to load fraud alerts:
      ${error.message}
    `
  }
}


document
  .querySelector('#analyzeButton')
  .addEventListener(
    'click',
    analyzeTransaction
  )

document
  .querySelector('#refreshAlerts')
  .addEventListener(
    'click',
    loadFraudSpikes
  )


loadMetrics()
loadFraudSpikes()