import { GlobalWorkerOptions } from 'pdfjs-dist/build/pdf.mjs';
import * as pdfjs from 'pdfjs-dist/build/pdf.mjs';
import { StateManager } from './stateManager.js';
import { Utils } from './utils.js';
import { KNOWLEDGE_BASE } from './knowledgeBase.js';
import { CreditorManager } from './creditorManager.js';
import { UserProfile } from './userProfile.js';
import { VehicleFinancingModule } from './vehicleFinancing.js';
import { BillEndorsement } from './billEndorsement.js';
import { CreditReportAnalysis } from './creditReportAnalysis.js';
import { FDCPA_Logger } from './fdcpaLogger.js';
import { DenialLetter } from './denialLetter.js';
import { PromiseToPayModule } from './promiseToPay.js';
import { Dashboard } from './dashboard.js';
import { initGlobalControls } from './script.js'; // Assuming script.js contains initGlobalControls

// Set up the PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = '/static/dist/pdf.worker.mjs';

document.addEventListener('DOMContentLoaded', () => {
    // --- CORE --- 
    const appState = new StateManager();
    const utils = new Utils(appState);

    // Global Search Elements
    const globalSearchInput = document.getElementById('globalSearchInput');
    const searchResultsDiv = document.getElementById('searchResults');

    utils.showLoader();

    try {
        // --- DASHBOARD ---
        const dashboard = new Dashboard(appState);

        // --- MODULES ---
        const creditorManager = new CreditorManager(appState, utils);
        const userProfile = new UserProfile(appState, utils, creditorManager);
        const vehicleFinancing = new VehicleFinancingModule(appState, KNOWLEDGE_BASE, utils, creditorManager);
        const billEndorsement = new BillEndorsement(appState, KNOWLEDGE_BASE, utils);
        const creditReportAnalysis = new CreditReportAnalysis(appState, KNOWLEDGE_BASE, utils, creditorManager);
        const fdcpaLogger = new FDCPA_Logger(appState, KNOWLEDGE_BASE, utils, creditorManager);
        const denialLetter = new DenialLetter(appState, KNOWLEDGE_BASE, utils);
        const promiseToPay = new PromiseToPayModule(appState, utils, creditorManager);

        // --- GLOBAL CONTROLS ---
        initGlobalControls(appState, utils, [
            vehicleFinancing,
            billEndorsement,
            creditReportAnalysis,
            fdcpaLogger,
            denialLetter,
            userProfile,
            creditorManager,
            promiseToPay
        ]);

        // Global Search Logic
        globalSearchInput.addEventListener('keyup', () => {
            const query = globalSearchInput.value.toLowerCase();
            if (query.length > 2) {
                const results = globalSearch(query, appState.getState(), KNOWLEDGE_BASE);
                displaySearchResults(results, searchResultsDiv);
            } else {
                searchResultsDiv.classList.add('hidden');
                searchResultsDiv.innerHTML = '';
            }
        });

        console.log('Sovereign Finance Cockpit Initialized');
    } catch (error) {
        console.error("Failed to initialize the application:", error);
        utils.setStatus("Application failed to load. Check the console for errors.", true);
    } finally {
        utils.hideLoader();
    }
});

function globalSearch(query, state, knowledgeBase) {
    const results = [];

    // Search Creditors
    state.creditors.forEach(creditor => {
        if (creditor.name.toLowerCase().includes(query) || creditor.address.toLowerCase().includes(query)) {
            results.push({ type: 'Creditor', name: creditor.name, description: creditor.address });
        }
    });

    // Search FDCPA Log
    state.fdcpaLog.forEach(log => {
        if (log.collector.toLowerCase().includes(query) || log.description.toLowerCase().includes(query)) {
            results.push({ type: 'FDCPA Violation', name: log.collector, description: `${knowledgeBase.FDCPA.violations[log.type].summary} on ${log.date}` });
        }
    });

    // Search Disputes
    state.disputes.forEach(dispute => {
        if (dispute.account_name.toLowerCase().includes(query) || dispute.account_number.toLowerCase().includes(query)) {
            results.push({ type: 'Dispute', name: dispute.account_name, description: `Account: ${dispute.account_number}, Status: ${dispute.status}` });
        }
    });

    // Add more search categories as needed (e.g., parsed credit report accounts, vehicle contract terms)

    return results;
}

function displaySearchResults(results, resultsContainer) {
    resultsContainer.innerHTML = '';
    if (results.length === 0) {
        resultsContainer.classList.add('hidden');
        return;
    }

    const ul = document.createElement('ul');
    results.forEach(result => {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${result.type}:</strong> ${result.name} - ${result.description}`;
        ul.appendChild(li);
    });

    resultsContainer.appendChild(ul);
    resultsContainer.classList.remove('hidden');
}