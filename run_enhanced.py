#!/usr/bin/env python3
import click
import sys
import os

# Aggiungi project root al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.logger import setup_logger
from src.utils.health_check import HealthChecker
from config import Config

logger = setup_logger()

@click.group()
def cli():
    """AI Social Bot - Enhanced CLI"""
    pass

@cli.command()
@click.option('--auto', is_flag=True, help='Modalità automatica')
def post(auto):
    """Genera e pubblica contenuto"""
    from src.main import main
    logger.info(f"Avvio post (auto={auto})")
    main(auto_mode=auto)

@cli.command()
def health():
    """Controlla salute del sistema"""
    logger.info("Esecuzione health check...")
    
    try:
        Config.validate()
        results = HealthChecker.run_all_checks(Config)
        
        click.echo(f"\n{'='*50}")
        click.echo(f"Status: {results['overall_status'].upper()}")
        click.echo(f"{'='*50}")
        
        for service, check in results['checks'].items():
            status_icon = "✅" if check['status'] == 'healthy' else "❌"
            click.echo(f"{status_icon} {service}: {check['status']}")
            if 'error' in check:
                click.echo(f"   Error: {check['error']}")
    except Exception as e:
        click.echo(f"❌ Health check failed: {e}")

@cli.command()
@click.option('--days', default=30, help='Giorni da analizzare')
def analytics(days):
    """Mostra analytics"""
    try:
        from src.utils.database_v2 import DatabaseV2
        db = DatabaseV2()
        stats = db.get_analytics(days)
        
        click.echo(f"\n📊 Analytics ultimi {days} giorni:")
        for platform_stats in stats['stats']:
            click.echo(f"\n{platform_stats['platform'].upper()}:")
            click.echo(f"  Post totali: {platform_stats['total_posts']}")
            click.echo(f"  Likes medi: {platform_stats['avg_likes']:.1f}")
            click.echo(f"  Reshares medi: {platform_stats['avg_reshares']:.1f}")
    except Exception as e:
        click.echo(f"❌ Errore analytics: {e}")

@cli.command()
def trending():
    """Mostra trending topics"""
    from src.content.trending import TrendingFinder
    
    click.echo("\n🔥 Trending Topics:\n")
    trends = TrendingFinder.combine_trends()
    
    for i, trend in enumerate(trends[:10], 1):
        click.echo(f"{i:2d}. {trend}")

if __name__ == '__main__':
    cli()
