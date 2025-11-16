import logging
from django.http import HttpResponseNotAllowed, JsonResponse, HttpResponse
from django.shortcuts import render

from timetable.models import Tag, Resource, FileVersion, Storage, Setting
from ..apps import TAG_CATEGORY_MAP, LOCAL_STORAGE_NAME

# Создаем логгер для текущего модуля
logger = logging.getLogger(__name__)


def timetable_list(request):
    if request.method != "GET":
        logger.warning(f"Method not allowed: {request.method} for timetable_list")
        return HttpResponseNotAllowed(["GET"])

    params = dict(request.GET.dict())
    type_timetable = params.get("type_timetable", None)

    logger.debug(f"Processing timetable_list request with params: {params}")

    if type_timetable == "lesson":
        type_tag = Tag.objects.filter(
            category="type_timetable", name__icontains="Занятия"
        ).first()
        logger.debug(f"Found lesson type tag: {type_tag}")

        match params.get("degree", None):
            case "master":
                tag = Tag.objects.filter(
                    category="degree", name__icontains="Магистратура"
                ).first()
                context = {
                    "head_title": "Расписания занятий для магистратуры",
                    "page_class": "master-page",
                    "schedule_title": "Расписания занятий для магистратуры",
                    "degree_title": "Магистратура",
                    "degree_card_class": "degree-card-master",
                    "degree_separator_class": "degree-card-separator-line-master",
                    "degree_image": "image/master_image.png",
                }
                logger.debug("Selected master degree for lessons")
            case "postgraduate":
                tag = Tag.objects.filter(
                    category="degree", name__icontains="Аспирантура"
                ).first()
                context = {
                    "head_title": "Расписания занятий для аспирантуры",
                    "page_class": "postgraduate-page",
                    "schedule_title": "Расписания занятий для аспирантуры",
                    "degree_title": "Аспирантура",
                    "degree_card_class": "degree-card-postgraduate",
                    "degree_separator_class": "degree-card-separator-line-postgraduate",
                    "degree_image": "image/phd_image.png",
                }
                logger.debug("Selected postgraduate degree for lessons")
            case _:
                tag = Tag.objects.filter(
                    category="degree", name__icontains="Бакалавриат, специалитет"
                ).first()
                context = {
                    "head_title": "Расписания занятий для бакалавриата (специалитета)",
                    "page_class": "bachelor-page",
                    "schedule_title": "Расписания занятий для бакалавриата (специалитета)",
                    "degree_title": "Бакалавриат (специалитет)",
                    "degree_card_class": "degree-card-bachelor",
                    "degree_separator_class": "degree-card-separator-line-bachelor",
                    "degree_image": "image/bachelor_image.png",
                }
                logger.debug("Selected bachelor degree for lessons (default)")
    elif type_timetable == "exam":
        type_tag = Tag.objects.filter(
            category="type_timetable", name__icontains="Экзамены"
        ).first()
        logger.debug(f"Found exam type tag: {type_tag}")

        match params.get("degree", None):
            case "master":
                tag = Tag.objects.filter(
                    category="degree", name__icontains="Магистратура"
                ).first()
                context = {
                    "head_title": "Расписания экзаменов для магистратуры",
                    "page_class": "master-page",
                    "schedule_title": "Расписания экзаменов для магистратуры",
                    "degree_title": "Магистратура",
                    "degree_card_class": "degree-card-master",
                    "degree_separator_class": "degree-card-separator-line-master",
                    "degree_image": "image/master_image.png",
                }
                logger.debug("Selected master degree for exams")
            case "postgraduate":
                tag = Tag.objects.filter(
                    category="degree", name__icontains="Аспирантура"
                ).first()
                context = {
                    "head_title": "Расписания экзаменов для аспирантуры",
                    "page_class": "postgraduate-page",
                    "schedule_title": "Расписания экзаменов для аспирантуры",
                    "degree_title": "Аспирантура",
                    "degree_card_class": "degree-card-postgraduate",
                    "degree_separator_class": "degree-card-separator-line-postgraduate",
                    "degree_image": "image/phd_image.png",
                }
                logger.debug("Selected postgraduate degree for exams")
            case _:
                tag = Tag.objects.filter(
                    category="degree", name__icontains="Бакалавриат, специалитет"
                ).first()
                context = {
                    "head_title": "Расписания экзаменов для бакалавриата (специалитета)",
                    "page_class": "bachelor-page",
                    "schedule_title": "Расписания экзаменов для бакалавриата (специалитета)",
                    "degree_title": "Бакалавриат (специалитет)",
                    "degree_card_class": "degree-card-bachelor",
                    "degree_separator_class": "degree-card-separator-line-bachelor",
                    "degree_image": "image/bachelor_image.png",
                }
                logger.debug("Selected bachelor degree for exams (default)")
    else:
        tag = None
        logger.warning(f"Unknown timetable type: {type_timetable}")

    if tag is None:
        logger.error("No tag found for the request parameters")
        return HttpResponse(status=500)

    context.update(
        {
            "type_required_key": type_tag.category,
            "type_required_value": type_tag.name,
            "degree_required_key": tag.category,
            "degree_required_value": tag.name,
        }
    )

    logger.info(f"Rendering timetable list with context: {context}")
    return render(request, "timetable_list.html", context)


def timetable_params(request):
    if request.method != "GET":
        logger.warning(f"Method not allowed: {request.method} for timetable_params")
        return HttpResponseNotAllowed(["GET"])

    tags = dict(request.GET)  # Получаем фильтры из GET-параметров
    logger.debug(f"Processing timetable_params request with tags: {tags}")

    resources = get_resource_by_tag(tags)
    logger.debug(f"Found {len(resources)} resources matching tags")

    # Получаем все теги, связанные с этими ресурсами
    related_tags = Tag.objects.filter(resources__in=resources).distinct()
    # Исключаем уже использованные фильтры
    for key, values in tags.items():
        related_tags = related_tags.exclude(category=key)

    # Получаем только уникальные названия категорий
    categories = set()
    for tag in related_tags:
        categories.add(tag.category)

    if len(categories) == 0:
        # Отправить список записей
        logger.debug("No more categories, returning files list")
        answer = get_files_list_answer(resources)
    else:
        # Отправить следующий селектор
        logger.debug(f"Found {len(categories)} more categories: {categories}")
        answer = get_new_selector_answer(categories, related_tags)

    logger.debug(f"Returning answer with result type: {answer.get('result')}")
    return JsonResponse(answer)


def get_resource_by_tag(tags):
    # Получаем начальный QuerySet всех ресурсов
    resources = Resource.objects.filter(deprecated=False)
    logger.debug(f"Initial resource count: {resources.count()}")

    # Фильтруем ресурсы для каждого переданного тега
    for key, values in tags.items():
        value = values[0]
        resources = resources.filter(tags__name=value, tags__category=key)
        logger.debug(f"After filtering by {key}={value}: {resources.count()} resources")

    return resources.distinct()


def get_new_selector_answer(categories, related_tags):
    # Определяем следующую категорию
    next_category = None
    for category in TAG_CATEGORY_MAP.keys():
        if category in categories:
            next_category = category
            break

    # Для категории определяем список тегов
    selector_items = get_selector_items(related_tags, next_category)
    logger.debug(
        f"Next category: {next_category}, selector items count: {len(selector_items)}"
    )

    # Формируем ответ
    answer = {
        "result": "selector",
        "selector_name": next_category,
        "selector_description": TAG_CATEGORY_MAP.get(next_category, "Выбрать"),
        "selector_items": selector_items,
    }

    return answer


def get_selector_items(tags, next_category):
    selector_items = list()
    for tag in tags:
        if tag.category == next_category:
            selector_items.append(tag.name)
    return selector_items


def get_files_list_answer(resources):
    files = []
    try:
        download_storage_type = Setting.objects.get(key="download_storage").value
        logger.debug(f"Using download storage type: {download_storage_type}")
    except Setting.DoesNotExist:
        download_storage_type = LOCAL_STORAGE_NAME
        logger.warning(
            f"Download storage setting not found, using default: {LOCAL_STORAGE_NAME}"
        )

    logger.info(f"Processing {len(resources)} resources for files list")

    for resource in resources:
        if resource.derived_from is None:
            file_versions = FileVersion.objects.filter(resource=resource).order_by(
                "-last_changed", "-timestamp"
            )
            last_version = file_versions.first()

            if file_versions.count() > 2:
                last_last_version = file_versions[1]
            else:
                last_last_version = None

            storages = Storage.objects.filter(file_version=last_version)
            view_urls = dict()
            archive_urls = dict()

            vis_resource = Resource.objects.filter(derived_from=resource).first()
            if vis_resource is not None:
                vis_file_version = FileVersion.objects.filter(
                    resource_id=vis_resource.id
                ).first()
                logger.debug(f"Found visualization resource for: {resource.name}")
            else:
                vis_file_version = None

            download_url = ""
            for storage in storages:
                storage_type = storage.storage_type
                if storage_type == download_storage_type:
                    download_url = storage.download_url

                resource_url = storage.resource_url
                if resource_url is not None:
                    view_urls[storage_type] = resource_url

                archive_url = storage.archive_url
                if archive_url is not None:
                    archive_urls[storage_type] = archive_url

                if vis_file_version is not None:
                    vis_view_urls = Storage.objects.filter(
                        storage_type="google drive", file_version_id=vis_file_version.id
                    ).first()
                    logger.debug(f"Visualization view URLs: {vis_view_urls}")
                else:
                    vis_view_urls = None

            res_data = {
                "name": resource.name,
                "last_update": last_version.last_changed.strftime("%d/%m/%Y %H:%M"),
                "download_url": download_url,
                "view_urls": view_urls,
                "archive_urls": archive_urls,
                "vis_view_urls": vis_view_urls.resource_url if vis_view_urls else None,
            }

            if last_last_version is not None:
                res_data["last_last_update"] = last_last_version.timestamp

            files.append(res_data)
            logger.debug(f"Added file data for: {resource.name}")

    # Формируем ответ
    answer = {"result": "files", "files": files}

    logger.info(f"Returning files list with {len(files)} files")
    return answer
