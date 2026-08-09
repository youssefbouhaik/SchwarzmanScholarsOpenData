.PHONY: plots transcripts lint app clean

plots:
	python generate_plots.py
	@echo "✓ analytics_dashboard/*.png regenerated"

transcripts:
	python scripts/video_pipeline.py
	@echo "✓ data/meta/*.json + data/transcripts/*.txt + ADMITTED_SCHOLAR_PROFILES.md updated (ultra pipeline)"

transcripts-legacy:
	python batch_processor.py
	@echo "✓ legacy batch_processor"

lint:
	python scripts/validate.py

app:
	streamlit run app.py

clean:
	rm -f temp_*.jpg temp_frame.jpg
	rm -f data/videos/*.part
