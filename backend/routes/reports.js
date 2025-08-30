const express = require('express');
const router = express.Router();
const { authenticateToken } = require('../middleware/auth');
const { reportValidation, handleValidationErrors } = require('../middleware/validation');
const reportsController = require('../controllers/reportsController');

// POST /api/reports - Submit a new incident report
router.post('/', authenticateToken, reportValidation, handleValidationErrors, reportsController.submitReport);

// GET /api/reports - Get all reports for the authenticated user
router.get('/', authenticateToken, reportsController.getUserReports);

// GET /api/reports/community - Get community reports (public)
router.get('/community', reportsController.getCommunityReports);

// GET /api/reports/:id - Get a specific report by ID
router.get('/:id', authenticateToken, reportsController.getReportById);

// PUT /api/reports/:id - Update a report (only by owner or admin)
router.put('/:id', authenticateToken, reportsController.updateReport);

// DELETE /api/reports/:id - Delete a report (only by owner or admin)
router.delete('/:id', authenticateToken, reportsController.deleteReport);

module.exports = router;
