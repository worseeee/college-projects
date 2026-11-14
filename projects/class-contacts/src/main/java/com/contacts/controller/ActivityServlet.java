package com.contacts.controller;

import com.contacts.entity.Activity;
import com.contacts.entity.User;
import com.contacts.service.ActivityService;

import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.List;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

@WebServlet("/activity")
public class ActivityServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private ActivityService activityService = new ActivityService();

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        doPost(request, response);
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        request.setCharacterEncoding("UTF-8");
        String action = request.getParameter("action");
        HttpSession session = request.getSession();
        User sessionUser = (User) session.getAttribute("sessionUser");
        String ipAddress = request.getRemoteAddr();

        if (action == null || "list".equals(action)) {
            List<Activity> activities = activityService.getActivityList();
            request.setAttribute("activities", activities);
            request.getRequestDispatcher("/jsp/activity.jsp").forward(request, response);
            
        } else if ("add".equals(action)) {
            Activity a = new Activity();
            a.setAdminId(sessionUser.getId());
            a.setTitle(request.getParameter("title"));
            a.setContent(request.getParameter("content"));
            try {
                a.setActivityTime(new SimpleDateFormat("yyyy-MM-dd'T'HH:mm").parse(request.getParameter("activityTime")));
            } catch (ParseException e) {
                e.printStackTrace();
            }
            activityService.addActivity(a, sessionUser.getRole(), ipAddress);
            response.sendRedirect(request.getContextPath() + "/activity?action=list");
            
        } else if ("delete".equals(action)) {
            int id = Integer.parseInt(request.getParameter("id"));
            activityService.deleteActivity(id, sessionUser.getId(), sessionUser.getRole(), ipAddress);
            response.sendRedirect(request.getContextPath() + "/activity?action=list");
            
        } else if ("enroll".equals(action)) {
            int id = Integer.parseInt(request.getParameter("id"));
            activityService.enrollActivity(id, sessionUser.getId(), ipAddress);
            response.sendRedirect(request.getContextPath() + "/activity?action=list");
            
        } else if ("cancel".equals(action)) {
            int id = Integer.parseInt(request.getParameter("id"));
            activityService.cancelEnrollment(id, sessionUser.getId(), ipAddress);
            response.sendRedirect(request.getContextPath() + "/activity?action=list");
            
        } else if ("enrollList".equals(action)) {
            int id = Integer.parseInt(request.getParameter("id"));
            List<User> users = activityService.getEnrollmentList(id);
            request.setAttribute("enrollUsers", users);
            request.getRequestDispatcher("/jsp/activity-enroll-list.jsp").forward(request, response);
        }
    }
}