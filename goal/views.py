from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound, ParseError


from django.db.models import Count
from tag.models import Tag

import datetime as dt
from datetime import datetime
from .models import Goal, AvailableDays, ImpossibleDates, DailyHourOfGoals
from .serializers import (
    GoalSerializer,
    GoalwithTodoSerializer,
    AvailableDaysSerializer,
    ImpossibleDatesSerializer,
)
from rest_framework.exceptions import ParseError


class GoalList(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # tag = request.query_params.get("tag", None)
        date_string = request.query_params.get("date", None)  # yyyy-mm-dd
        day_num = request.query_params.get(
            "day", None
        )  # 0~6 사이 숫자. 0: 월, 1: 화, 2: 수, 3: 목, 4: 금, 5: 토, 6: 일

        try:
            if date_string:
                date = datetime.strptime(date_string, "%Y-%m-%d").date()
            else:
                date = None
        except ValueError:
            raise ParseError(
                "Invalid date format. Date should be in the format 'YYYY-MM-DD'."
            )

        if day_num is not None:
            try:
                day_num = int(day_num)
                days_of_week = [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                ]
                day = days_of_week[day_num]
            except (ValueError, IndexError):
                raise ParseError(
                    "Invalid day value. Day should be an integer between 0 and 6."
                )
        # if tag is not None:
        #     goals = Goal.objects.filter(tag=tag, user=request.user)
        # else:
        #     goals = Goal.objects.filter(user=request.user)
        goals = Goal.objects.filter(user=request.user)

        def is_displayed_on_date(goal):
            if not goal.is_scheduled:
                return False
            start_at = goal.start_at
            finish_at = goal.finish_at
            if start_at > date or finish_at < date:
                return False
            if AvailableDays.objects.filter(goal=goal).exists():
                if (
                    day is not None
                    and getattr(AvailableDays.objects.get(goal=goal), str(day)) == False
                ):
                    return False
            else:
                return False
            # if ImpossibleDates.objects.filter(goal=goal).exists():
            #     for impossibledates in ImpossibleDates.objects.filter(goal=goal):
            #         if impossibledates.date == date:
            #             return False
            return True

        if (
            date is not None and day_num is not None
        ):  # 날짜, 요일이 query parameter로 들어온 경우 -> 요일 상세 -> impossible day로 선택된 날짜라도 리턴함.
            displayed_goals = []
            for goal in goals:
                if is_displayed_on_date(goal):
                    displayed_goals.append(goal.id)
            goals = goals.filter(id__in=displayed_goals)
        # else : #날짜, 요일이 query parameter로 안들어옴. 전체 goal을 전달하는 경우. 내 목표, 캘린더 -> 태그로 필터링되지 않은 전체 goal
        serializer = GoalSerializer(goals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(
        self, request
    ):  # 최초의 목표 추가. 캘린더에도 추가하는 경우 "add_calendar" is not None. 추가된 목표를 캘린더에 추가하는 로직은 GoalDetail에서 구현
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        add_calendar = request.query_params.get("add_calendar", None)
        user = request.user
        tag_id = request.data.get(
            "tag_id", None
        )  # tag_title로 받아오는 것이 아닌 tag_id로 받아오는 것으로 수정
        try:
            tag = Tag.objects.get(user=user, id=tag_id)  # tag_id로 검색하는 것으로 수정
        except Tag.DoesNotExist:
            raise ParseError("Invalid tag value. Tag does not exist.")
        title = request.data.get("title", None)

        try:
            if add_calendar:
                start_at_string = request.data.get("start_at", None)
                start_at = datetime.strptime(start_at_string, "%Y-%m-%d").date()
                finish_at_string = request.data.get("finish_at", None)
                finish_at = datetime.strptime(finish_at_string, "%Y-%m-%d").date()
                is_scheduled = True
                available_days_list = request.data.get("available_days", None)
                residual_time = request.data.get("estimated_time", None)
                estimated_time = request.data.get("estimated_time", None)
                goal = Goal.objects.create(
                    user=user,
                    tag_id=tag_id,  # tag_id 입력으로 수정
                    title=title,
                    start_at=start_at,
                    finish_at=finish_at,
                    is_scheduled=is_scheduled,
                    residual_time=residual_time,
                    estimated_time=estimated_time,
                    cumulative_time=0,
                    progress_rate=0,
                )
                if available_days_list is not None and len(available_days_list) == 7:
                    AvailableDays.objects.create(
                        goal=goal,
                        monday=available_days_list[0],
                        tuesday=available_days_list[1],
                        wednesday=available_days_list[2],
                        thursday=available_days_list[3],
                        friday=available_days_list[4],
                        saturday=available_days_list[5],
                        sunday=available_days_list[6],
                    )
                else:
                    raise ParseError(
                        f"""{available_days_list}/n
                        Invalid available_days value. available_days should be a list of length 7."""
                    )
            else:
                goal = Goal.objects.create(user=user, tag_id=tag_id, title=title)
        except (ValueError, KeyError):
            raise ParseError(
                "Invalid date format. Date should be in the format 'YYYY-MM-DD'."
            )
        except Exception as e:
            raise ParseError(str(e))

        serializer = GoalSerializer(goal)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GoalDetail(APIView):
    def get(self, request, goal_id):  # 특정 목표의 상세 데이터
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            goal = Goal.objects.get(user=request.user, id=goal_id)
        except ObjectDoesNotExist:
            raise NotFound("Goal not found.")
        serializer = GoalwithTodoSerializer(goal)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, goal_id):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            goal = Goal.objects.get(id=goal_id)
        except ObjectDoesNotExist:
            raise NotFound("Goal not found.")

        daily_check = request.query_params.get("daily_check", None)
        add_calendar = request.query_params.get("add_calendar", None)
        rollback = request.query_params.get("rollback", None)
        # 발바닥 누르는 경우(당일 일정 완료)
        if daily_check is not None:
            try:
                goal.prev_update_at = goal.update_at
                goal.update_at = dt.date.today()
                goal.prev_residual_time = goal.residual_time
                goal.residual_time = goal.residual_time - request.data.get("daily_time")
                goal.prev_cumulative_time = goal.cumulative_time
                goal.cumulative_time = goal.cumulative_time + request.data.get(
                    "daily_time"
                )
                goal.prev_progress_rate = goal.progress_rate
                goal.progress_rate = request.data.get("progress_rate", None)
                if goal.progress_rate == 100:
                    goal.is_completed = True
                DailyHourOfGoals.objects.create(
                    user=request.user,
                    goal=goal,
                    hour=request.data.get("daily_time"),
                    date=dt.date.today(),
                )
                goal.save()
            except (ValueError, KeyError):
                raise ParseError(
                    "Invalid request body. Check your data types and keys."
                )
        # calendar 추가하는 경우.
        elif add_calendar is not None:
            try:
                goal.is_scheduled = True
                start_at_string = request.data.get("start_at", None)
                start_at = datetime.strptime(start_at_string, "%Y-%m-%d").date()
                goal.start_at = start_at
                finish_at_string = request.data.get("finish_at", None)
                finish_at = datetime.strptime(finish_at_string, "%Y-%m-%d").date()
                goal.finish_at = finish_at
                available_days_list = request.data.get("available_days", None)
                if available_days_list is not None and len(available_days_list) == 7:
                    AvailableDays.objects.create(
                        goal=goal,
                        monday=available_days_list[0],
                        tuesday=available_days_list[1],
                        wednesday=available_days_list[2],
                        thursday=available_days_list[3],
                        friday=available_days_list[4],
                        saturday=available_days_list[5],
                        sunday=available_days_list[6],
                    )
                else:
                    raise ParseError(
                        "Invalid available_days value. available_days should be a list of length 7."
                    )
                goal.residual_time = request.data.get("estimated_time", None)
                goal.estimated_time = request.data.get("estimated_time", None)
                goal.save()
            except (ValueError, KeyError):
                raise ParseError(
                    "Invalid request body. Check your data types and keys."
                )
        # 완료된 목표를 롤백하는 경우
        elif rollback is not None:
            DailyHourOfGoals.objects.get(
                user=request.user, goal=goal, date=goal.update_at
            ).delete()
            goal.update_at = goal.prev_update_at
            goal.progress_rate = goal.prev_progress_rate
            goal.cumulative_time = goal.prev_cumulative_time
            goal.residual_time = goal.prev_residual_time
            goal.save()
        # 상세에서 수정하는 경우
        elif daily_check is None and add_calendar is None and rollback is None:
            try:
                goal.title = request.data.get("title", None)
                tag_title = request.data.get("tag", None)
                tag = Tag.objects.get(user=request.user, title=tag_title)
                goal.tag = tag
                if goal.is_scheduled:
                    start_at_string = request.data.get("start_at", None)
                    start_at = datetime.strptime(start_at_string, "%Y-%m-%d").date()
                    goal.start_at = start_at
                    finish_at_string = request.data.get("finish_at", None)
                    finish_at = datetime.strptime(finish_at_string, "%Y-%m-%d").date()
                    goal.finish_at = finish_at
                    goal.residual_time = request.data.get("residual_time", None)
                    goal.progress_rate = request.data.get("progress_rate", None)
                    if goal.progress_rate == 100:
                        goal.is_completed = True

                    available_days_list = request.data.get("available_days", None)
                    if (
                        available_days_list is not None
                        and len(available_days_list) == 7
                    ):
                        available_days = AvailableDays.objects.get(goal=goal)
                        available_days.monday = available_days_list[0]
                        available_days.tuesday = available_days_list[1]
                        available_days.wednesday = available_days_list[2]
                        available_days.thursday = available_days_list[3]
                        available_days.friday = available_days_list[4]
                        available_days.saturday = available_days_list[5]
                        available_days.sunday = available_days_list[6]
                        available_days.save()
                    else:
                        raise ParseError(
                            "Invalid available_days value. available_days should be a list of length 7."
                        )
                goal.save()
            except (ValueError, KeyError):
                raise ParseError(
                    "Invalid request body. Check your data types and keys."
                )
            except ObjectDoesNotExist:
                raise NotFound("Tag not found.")

        serializer = GoalSerializer(goal)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, goal_id):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        calendar_only = request.query_params.get("calendar_only", None)
        goal = Goal.objects.get(id=goal_id)
        if calendar_only is not None:
            goal.is_scheduled = False
            AvailableDays.objects.get(goal=goal).delete()
            DailyHourOfGoals.objects.filter(user=request.user, goal=goal).delete()
        else:
            goal.delete()
        return Response("삭제되었습니다.", status=status.HTTP_204_NO_CONTENT)


class ImpossibleDatesOfGoal(APIView):
    def get(self, request, goal_id):  # 특정 목표의 불가능한 날짜 얻기. 그냥 해당 목표에 대한 모든 정보 담고 있음.
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            goal = Goal.objects.get(id=goal_id)
        except ObjectDoesNotExist:
            raise NotFound("Goal not found.")

        serializer = GoalSerializer(goal)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, goal_id):  # 불가능한 날짜 체크
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            goal = Goal.objects.get(id=goal_id)
        except ObjectDoesNotExist:
            raise NotFound("Goal not found.")

        if not goal.is_scheduled:
            return Response(
                {"detail": "This goal is not scheduled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        date_string = request.data.get("date", None)
        if date_string is None:
            raise ParseError("Missing 'date' parameter in the request body.")

        try:
            date = datetime.strptime(date_string, "%Y-%m-%d").date()
        except ValueError:
            raise ParseError("Invalid date format. Use 'YYYY-MM-DD' format.")

        if ImpossibleDates.objects.filter(goal_id=goal_id, date=date).exists():
            return Response(
                {"detail": "This date is already registered."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        impossibleDate = ImpossibleDates.objects.create(goal_id=goal_id, date=date)
        serializer = ImpossibleDatesSerializer(impossibleDate)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, goal_id):  # 불가능한 날짜 삭제
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        date_string = request.data.get("date")
        if date_string is None:
            raise ParseError("Missing 'date' parameter in the request body.")

        try:
            date = datetime.strptime(date_string, "%Y-%m-%d").date()
        except ValueError:
            raise ParseError("Invalid date format. Use 'YYYY-MM-DD' format.")

        try:
            goal = Goal.objects.get(id=goal_id)
        except ObjectDoesNotExist:
            raise NotFound("Goal not found.")

        impossibleDate = ImpossibleDates.objects.filter(goal=goal, date=date)
        if not impossibleDate.exists():
            raise NotFound("Impossible date not found.")

        impossibleDate.delete()
        return Response("Deleted successfully.", status=status.HTTP_204_NO_CONTENT)
