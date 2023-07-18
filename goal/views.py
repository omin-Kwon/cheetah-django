from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Count
from tag.models import Tag

import datetime
from .models import Goal
from .serializers import GoalSerializer, GoalwithTodoSerializer


class GoalList(APIView):
    def get(self, request):
        tag = request.query_params.get("tag", None)
        date = request.query_params.get("date", None)  #'20230731'
        day = request.query_params.get("day", None)  #'0~6으로 보내기'
        if tag is not None:
            goals = Goal.objects.filter(tag=tag, user=request.user)
        else:
            goals = Goal.objects.filter(user=request.user)

        def is_active_goal(goal):
            if not goal.is_schedule:
                return False
            start_at = goal.start_at
            finish_at = goal.finish_at
            if start_at > date or finish_at < date:
                return False
            if goal.avaliable_days[day] == "0":
                return False
            if goal.exception_days.filter(
                date=datetime.datetime.strptime(date, "%Y%m%d")
            ).exists():
                return False
            return True

        if date is not None:
            active_goal = []
            for goal in goals:
                if is_active_goal(goal):
                    active_goal.append(goal.id)
            goals = goals.filter(id__in=active_goal)
        serializer = GoalSerializer(goals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):  # calendar에도 추가하기 query param
        add_calendar = request.query_params.get("add_calendar", None)
        user = request.user
        tag = request.data.get("tag", None)
        title = request.data.get("title", None)
        if add_calendar is not None:
            start_at = request.data.get("start_at", None)
            finish_at = request.data.get("finish_at", None)
            is_scheduled = True
            avaliable_days = request.data.get("avaliable_days", None)
            residual_time = request.data.get("estimated_time", None)
            estimated_time = request.data.get("estimated_time", None)
            goal = Goal.objects.create(
                user=user,
                tag=tag,
                title=title,
                start_at=start_at,
                finish_at=finish_at,
                is_scheduled=is_scheduled,
                avaliable_days=avaliable_days,
                residual_time=residual_time,
                estimated_time=estimated_time,
                cumulative_time=0,
                progress_rate=0,
            )
        else:
            goal = Goal.objects.create(user=user, tag=tag, title=title)
        serializer = GoalSerializer(goal)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GoalDetail(APIView):
    def get(self, request, goal_id):
        goal = Goal.objects.get(user=request.user, id=goal_id)
        serializer = GoalwithTodoSerializer(goal)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, goal_id):
        goal = Goal.objects.get(id=goal_id)
        daily_check = request.query_params.get("daily_check", None)
        add_calendar = request.query_params.get("add_calendar", None)
        # 발바닥 누르는 경우
        if daily_check is not None:
            goal.prev_update_at = goal.update_at
            goal.update_at = datetime.date.today()
            goal.prev_residual_time = goal.residual_time
            goal.residual_time = goal.residual_time - int(
                request.data.get("daily_time", None)
            )
            goal.prev_cumulative_time = goal.cumulative_time
            goal.cumulative_time = goal.cumulative_time + int(
                request.data.get("daily_time", None)
            )  # daily time을 body에 추가로 담자.
            goal.prev_progress_rate = goal.progress_rate
            goal.progress_rate = request.data.get("progress_rate", None)
            goal.is_completed = request.data.get("is_completed", None)
            goal.save()
        # 상세에서 수정하는 경우
        elif add_calendar is None:
            goal.title = request.data.get("title", None)
            goal.tag = request.data.get("tag", None)
            goal.start_at = request.data.get("start_at", None)
            goal.finish_at = request.data.get("finish_at", None)
            goal.avaliable_days = request.data.get("avaliable_days", None)
            goal.residual_time = request.data.get("residual_time", None)
            goal.prev_progress_rate = goal.progress_rate
            goal.progress_rate = request.data.get("progress_rate", None)
            goal.save()
        # calendar 추가 경우.
        else:
            goal.start_at = request.data.get("start_at", None)
            goal.finish_at = request.data.get("finish_at", None)
            goal.is_scheduled = True
            goal.avaliable_days = request.data.get("avaliable_days", None)
            goal.residual_time = request.data.get("estimated_time", None)
            goal.estimated_time = request.data.get("estimated_time", None)
            goal.save()
        serializer = GoalSerializer(goal)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, goal_id):
        goal = Goal.objects.get(id=goal_id)
        goal.delete()
        return Response("삭제되었습니다.", status=status.HTTP_204_NO_CONTENT)
