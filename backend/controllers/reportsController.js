const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

// Submit a new incident report
const submitReport = async (req, res) => {
  try {
    const { category, description, location, photo } = req.body;
    const userId = req.user.id;

    // Validate required fields
    if (!category || !description || !location || !photo) {
      return res.status(400).json({
        success: false,
        message: 'Missing required fields: category, description, location, and photo are required'
      });
    }

    // Create the report in the database
    const report = await prisma.report.create({
      data: {
        category,
        description,
        latitude: location.latitude,
        longitude: location.longitude,
        address: location.address,
        photo: photo, // Store base64 photo
        status: 'PENDING',
        userId: userId,
        createdAt: new Date(),
        updatedAt: new Date()
      },
      include: {
        user: {
          select: {
            id: true,
            name: true,
            email: true
          }
        }
      }
    });

    // Award points to user for submitting a report
    const pointsToAward = 10; // Base points for submitting a report
    await prisma.user.update({
      where: { id: userId },
      data: {
        points: {
          increment: pointsToAward
        }
      }
    });

    res.status(201).json({
      success: true,
      message: 'Report submitted successfully',
      data: {
        report: {
          id: report.id,
          category: report.category,
          description: report.description,
          location: {
            latitude: report.latitude,
            longitude: report.longitude,
            address: report.address
          },
          status: report.status,
          createdAt: report.createdAt,
          user: report.user
        },
        pointsAwarded: pointsToAward
      }
    });

  } catch (error) {
    console.error('Error submitting report:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while submitting report'
    });
  }
};

// Get all reports for the authenticated user
const getUserReports = async (req, res) => {
  try {
    const userId = req.user.id;
    const { page = 1, limit = 10, status } = req.query;

    const skip = (page - 1) * limit;
    const whereClause = { userId };

    if (status) {
      whereClause.status = status.toUpperCase();
    }

    const reports = await prisma.report.findMany({
      where: whereClause,
      skip: parseInt(skip),
      take: parseInt(limit),
      orderBy: {
        createdAt: 'desc'
      },
      include: {
        user: {
          select: {
            id: true,
            name: true,
            email: true
          }
        }
      }
    });

    const totalReports = await prisma.report.count({
      where: whereClause
    });

    res.json({
      success: true,
      data: {
        reports,
        pagination: {
          currentPage: parseInt(page),
          totalPages: Math.ceil(totalReports / limit),
          totalReports,
          hasNextPage: skip + reports.length < totalReports,
          hasPrevPage: page > 1
        }
      }
    });

  } catch (error) {
    console.error('Error fetching user reports:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while fetching reports'
    });
  }
};

// Get community reports (public)
const getCommunityReports = async (req, res) => {
  try {
    const { page = 1, limit = 10, category, status } = req.query;

    const skip = (page - 1) * limit;
    const whereClause = {};

    if (category) {
      whereClause.category = category;
    }

    if (status) {
      whereClause.status = status.toUpperCase();
    }

    const reports = await prisma.report.findMany({
      where: whereClause,
      skip: parseInt(skip),
      take: parseInt(limit),
      orderBy: {
        createdAt: 'desc'
      },
      include: {
        user: {
          select: {
            id: true,
            name: true
          }
        }
      }
    });

    const totalReports = await prisma.report.count({
      where: whereClause
    });

    res.json({
      success: true,
      data: {
        reports,
        pagination: {
          currentPage: parseInt(page),
          totalPages: Math.ceil(totalReports / limit),
          totalReports,
          hasNextPage: skip + reports.length < totalReports,
          hasPrevPage: page > 1
        }
      }
    });

  } catch (error) {
    console.error('Error fetching community reports:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while fetching community reports'
    });
  }
};

// Get a specific report by ID
const getReportById = async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;

    const report = await prisma.report.findUnique({
      where: { id: parseInt(id) },
      include: {
        user: {
          select: {
            id: true,
            name: true,
            email: true
          }
        }
      }
    });

    if (!report) {
      return res.status(404).json({
        success: false,
        message: 'Report not found'
      });
    }

    // Check if user has permission to view this report
    if (report.userId !== userId && req.user.role !== 'ADMIN') {
      return res.status(403).json({
        success: false,
        message: 'Access denied. You can only view your own reports.'
      });
    }

    res.json({
      success: true,
      data: { report }
    });

  } catch (error) {
    console.error('Error fetching report:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while fetching report'
    });
  }
};

// Update a report
const updateReport = async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;
    const { description, category, status } = req.body;

    // Check if report exists
    const existingReport = await prisma.report.findUnique({
      where: { id: parseInt(id) }
    });

    if (!existingReport) {
      return res.status(404).json({
        success: false,
        message: 'Report not found'
      });
    }

    // Check if user has permission to update this report
    if (existingReport.userId !== userId && req.user.role !== 'ADMIN') {
      return res.status(403).json({
        success: false,
        message: 'Access denied. You can only update your own reports.'
      });
    }

    // Prepare update data
    const updateData = {
      updatedAt: new Date()
    };

    if (description) updateData.description = description;
    if (category) updateData.category = category;
    if (status && req.user.role === 'ADMIN') updateData.status = status.toUpperCase();

    const updatedReport = await prisma.report.update({
      where: { id: parseInt(id) },
      data: updateData,
      include: {
        user: {
          select: {
            id: true,
            name: true,
            email: true
          }
        }
      }
    });

    res.json({
      success: true,
      message: 'Report updated successfully',
      data: { report: updatedReport }
    });

  } catch (error) {
    console.error('Error updating report:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while updating report'
    });
  }
};

// Delete a report
const deleteReport = async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;

    // Check if report exists
    const existingReport = await prisma.report.findUnique({
      where: { id: parseInt(id) }
    });

    if (!existingReport) {
      return res.status(404).json({
        success: false,
        message: 'Report not found'
      });
    }

    // Check if user has permission to delete this report
    if (existingReport.userId !== userId && req.user.role !== 'ADMIN') {
      return res.status(403).json({
        success: false,
        message: 'Access denied. You can only delete your own reports.'
      });
    }

    await prisma.report.delete({
      where: { id: parseInt(id) }
    });

    res.json({
      success: true,
      message: 'Report deleted successfully'
    });

  } catch (error) {
    console.error('Error deleting report:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while deleting report'
    });
  }
};

module.exports = {
  submitReport,
  getUserReports,
  getCommunityReports,
  getReportById,
  updateReport,
  deleteReport
};
